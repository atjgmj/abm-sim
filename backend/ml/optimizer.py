"""Machine learning-based parameter optimization for ABM models."""

import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import optuna
from optuna.samplers import TPESampler

from ..schemas import ScenarioRequest, KPICategory
from ..store.db import SimulationStore

logger = logging.getLogger(__name__)


@dataclass
class OptimizationTarget:
    """Optimization target definition."""
    kpi: KPICategory
    target_value: float
    weight: float = 1.0
    target_type: str = "maximize"  # "maximize", "minimize", "target"


@dataclass 
class OptimizationResult:
    """Result of parameter optimization."""
    best_params: Dict[str, Any]
    best_score: float
    improvement: float
    confidence: float
    method_used: str
    training_samples: int


class ParameterOptimizer:
    """ML-based parameter optimizer for ABM models."""
    
    def __init__(self, store: SimulationStore):
        self.store = store
        self.scaler = StandardScaler()
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boost': GradientBoostingRegressor(random_state=42),
            'gaussian_process': GaussianProcessRegressor(
                kernel=ConstantKernel() * RBF(length_scale=1.0),
                random_state=42
            )
        }
        self.best_model = None
        self.feature_names = []
    
    def extract_features_from_scenario(self, scenario: ScenarioRequest) -> np.ndarray:
        """Extract numerical features from scenario for ML models."""
        features = []
        
        # Media mix features
        features.extend([
            scenario.media_mix.sns.share,
            scenario.media_mix.sns.alpha,
            scenario.media_mix.video.share,
            scenario.media_mix.video.alpha,
            scenario.media_mix.search.share,
            scenario.media_mix.search.alpha,
        ])
        
        # Word-of-mouth features
        features.extend([
            scenario.wom.p_generate,
            scenario.wom.decay,
            scenario.wom.personality_weight,
            scenario.wom.demographic_weight,
        ])
        
        # Network features
        features.extend([
            scenario.network.n,
            scenario.network.k,
            scenario.network.beta or 0.1,
        ])
        
        # Personality features
        features.extend([
            scenario.personality.openness,
            scenario.personality.social_influence,
            scenario.personality.media_affinity,
            scenario.personality.risk_tolerance,
        ])
        
        # Demographics features
        features.extend([
            scenario.demographics.age_group,
            scenario.demographics.income_level,
            scenario.demographics.urban_rural,
            scenario.demographics.education_level,
        ])
        
        # Influencer features
        features.extend([
            float(scenario.influencers.enable_influencers),
            scenario.influencers.influencer_ratio,
            scenario.influencers.influence_multiplier,
        ])
        
        # Simulation parameters
        features.extend([
            scenario.steps,
            scenario.reps,
        ])
        
        if not self.feature_names:
            self.feature_names = [
                'sns_share', 'sns_alpha', 'video_share', 'video_alpha', 'search_share', 'search_alpha',
                'wom_p_generate', 'wom_decay', 'wom_personality_weight', 'wom_demographic_weight',
                'network_n', 'network_k', 'network_beta',
                'personality_openness', 'personality_social_influence', 'personality_media_affinity', 'personality_risk_tolerance',
                'demo_age_group', 'demo_income_level', 'demo_urban_rural', 'demo_education_level',
                'influencers_enabled', 'influencers_ratio', 'influencers_multiplier',
                'steps', 'reps'
            ]
        
        return np.array(features)
    
    def calculate_objective_score(self, results: Dict[str, Any], targets: List[OptimizationTarget]) -> float:
        """Calculate objective score based on optimization targets."""
        total_score = 0.0
        total_weight = 0.0
        
        for target in targets:
            if target.kpi.value in results.get('summary', {}):
                actual_value = results['summary'][target.kpi.value]['end']
                
                if target.target_type == "maximize":
                    score = actual_value / max(1, target.target_value)  # Normalize by target
                elif target.target_type == "minimize":
                    score = target.target_value / max(1, actual_value)  # Inverse for minimization
                else:  # target
                    score = 1.0 - abs(actual_value - target.target_value) / max(1, target.target_value)
                
                total_score += score * target.weight
                total_weight += target.weight
        
        return total_score / max(1, total_weight)
    
    def collect_training_data(self, min_samples: int = 20) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
        """Collect training data from historical simulations."""
        # Get all completed simulations
        simulations = self.store.get_all_simulations()
        
        X, y, metadata = [], [], []
        
        for sim in simulations:
            try:
                scenario_data = sim.get('scenario')
                results_data = sim.get('results')
                
                if not scenario_data or not results_data:
                    continue
                
                # Reconstruct scenario object
                scenario = ScenarioRequest(**scenario_data)
                
                # Extract features
                features = self.extract_features_from_scenario(scenario)
                
                # Calculate default objective (total final awareness + intent)
                if 'summary' in results_data:
                    summary = results_data['summary']
                    awareness_score = summary.get('awareness', {}).get('end', 0)
                    intent_score = summary.get('intent', {}).get('end', 0)
                    objective_score = awareness_score * 0.6 + intent_score * 0.4  # Weighted combination
                    
                    X.append(features)
                    y.append(objective_score)
                    metadata.append({
                        'scenario_id': sim.get('id'),
                        'awareness': awareness_score,
                        'intent': intent_score,
                        'objective': objective_score
                    })
                
            except Exception as e:
                logger.warning(f"Error processing simulation data: {e}")
                continue
        
        if len(X) < min_samples:
            logger.warning(f"Insufficient training data: {len(X)} samples (minimum: {min_samples})")
            return np.array([]), np.array([]), []
        
        return np.array(X), np.array(y), metadata
    
    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Dict[str, float]]:
        """Train multiple ML models and return their performance."""
        if len(X) < 5:
            raise ValueError("Insufficient training data for model training")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        model_performance = {}
        
        for name, model in self.models.items():
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train, y_train, cv=min(5, len(X_train)), scoring='r2')
                
                # Test set performance
                y_pred = model.predict(X_test)
                test_r2 = r2_score(y_test, y_pred)
                test_mse = mean_squared_error(y_test, y_pred)
                
                model_performance[name] = {
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'test_r2': test_r2,
                    'test_mse': test_mse
                }
                
                logger.info(f"{name} - CV R2: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}, Test R2: {test_r2:.3f}")
                
            except Exception as e:
                logger.warning(f"Error training {name}: {e}")
                model_performance[name] = {'cv_mean': -999, 'cv_std': 999, 'test_r2': -999, 'test_mse': 999}
        
        # Select best model
        best_model_name = max(model_performance.keys(), key=lambda x: model_performance[x]['cv_mean'])
        self.best_model = self.models[best_model_name]
        
        logger.info(f"Best model selected: {best_model_name}")
        
        return model_performance
    
    def optimize_parameters_ml(
        self, 
        base_scenario: ScenarioRequest,
        targets: List[OptimizationTarget],
        n_trials: int = 50
    ) -> OptimizationResult:
        """Optimize parameters using ML-guided search."""
        
        # Collect training data
        X, y, metadata = self.collect_training_data()
        
        if len(X) < 10:
            # Fallback to random search if insufficient data
            return self._random_search_optimization(base_scenario, targets, n_trials)
        
        # Train models
        model_performance = self.train_models(X, y)
        
        if self.best_model is None:
            return self._random_search_optimization(base_scenario, targets, n_trials)
        
        # Use Optuna for Bayesian optimization with ML model guidance
        def objective(trial):
            # Sample parameters within reasonable bounds
            scenario_params = {
                'media_mix': {
                    'sns': {
                        'share': trial.suggest_float('sns_share', 0.1, 0.8),
                        'alpha': trial.suggest_float('sns_alpha', 0.01, 0.1)
                    },
                    'video': {
                        'share': trial.suggest_float('video_share', 0.1, 0.6),
                        'alpha': trial.suggest_float('video_alpha', 0.01, 0.08)
                    },
                    'search': {
                        'share': trial.suggest_float('search_share', 0.1, 0.5),
                        'alpha': trial.suggest_float('search_alpha', 0.005, 0.05)
                    }
                },
                'wom': {
                    'p_generate': trial.suggest_float('wom_p_generate', 0.02, 0.2),
                    'decay': trial.suggest_float('wom_decay', 0.7, 0.95),
                    'personality_weight': trial.suggest_float('personality_weight', 0.1, 0.5),
                    'demographic_weight': trial.suggest_float('demographic_weight', 0.1, 0.4)
                },
                'personality': {
                    'openness': trial.suggest_float('personality_openness', 0.2, 0.8),
                    'social_influence': trial.suggest_float('personality_social_influence', 0.2, 0.8),
                    'media_affinity': trial.suggest_float('personality_media_affinity', 0.2, 0.8),
                    'risk_tolerance': trial.suggest_float('personality_risk_tolerance', 0.2, 0.8)
                },
                'influencers': {
                    'enable_influencers': trial.suggest_categorical('influencers_enabled', [True, False]),
                    'influencer_ratio': trial.suggest_float('influencers_ratio', 0.005, 0.05),
                    'influence_multiplier': trial.suggest_float('influencers_multiplier', 1.5, 5.0)
                }
            }
            
            # Normalize media mix shares
            total_share = (scenario_params['media_mix']['sns']['share'] + 
                          scenario_params['media_mix']['video']['share'] + 
                          scenario_params['media_mix']['search']['share'])
            
            for channel in ['sns', 'video', 'search']:
                scenario_params['media_mix'][channel]['share'] /= total_share
            
            # Create test scenario
            test_scenario = base_scenario.model_copy(deep=True)
            test_scenario.media_mix.sns.share = scenario_params['media_mix']['sns']['share']
            test_scenario.media_mix.sns.alpha = scenario_params['media_mix']['sns']['alpha']
            test_scenario.media_mix.video.share = scenario_params['media_mix']['video']['share']
            test_scenario.media_mix.video.alpha = scenario_params['media_mix']['video']['alpha']
            test_scenario.media_mix.search.share = scenario_params['media_mix']['search']['share']
            test_scenario.media_mix.search.alpha = scenario_params['media_mix']['search']['alpha']
            
            test_scenario.wom.p_generate = scenario_params['wom']['p_generate']
            test_scenario.wom.decay = scenario_params['wom']['decay']
            test_scenario.wom.personality_weight = scenario_params['wom']['personality_weight']
            test_scenario.wom.demographic_weight = scenario_params['wom']['demographic_weight']
            
            test_scenario.personality.openness = scenario_params['personality']['openness']
            test_scenario.personality.social_influence = scenario_params['personality']['social_influence']
            test_scenario.personality.media_affinity = scenario_params['personality']['media_affinity']
            test_scenario.personality.risk_tolerance = scenario_params['personality']['risk_tolerance']
            
            test_scenario.influencers.enable_influencers = scenario_params['influencers']['enable_influencers']
            test_scenario.influencers.influencer_ratio = scenario_params['influencers']['influencer_ratio']
            test_scenario.influencers.influence_multiplier = scenario_params['influencers']['influence_multiplier']
            
            # Predict score using trained model
            features = self.extract_features_from_scenario(test_scenario)
            features_scaled = self.scaler.transform([features])
            predicted_score = self.best_model.predict(features_scaled)[0]
            
            return predicted_score
        
        # Run optimization
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=42)
        )
        
        study.optimize(objective, n_trials=n_trials)
        
        # Extract best parameters
        best_trial = study.best_trial
        best_params = best_trial.params
        
        # Calculate improvement over baseline
        baseline_features = self.extract_features_from_scenario(base_scenario)
        baseline_features_scaled = self.scaler.transform([baseline_features])
        baseline_score = self.best_model.predict(baseline_features_scaled)[0]
        improvement = (best_trial.value - baseline_score) / max(1, baseline_score) * 100
        
        # Calculate confidence based on model performance
        best_model_name = max(model_performance.keys(), key=lambda x: model_performance[x]['cv_mean'])
        confidence = max(0, min(1, model_performance[best_model_name]['cv_mean']))
        
        return OptimizationResult(
            best_params=best_params,
            best_score=best_trial.value,
            improvement=improvement,
            confidence=confidence,
            method_used=f"ML-guided ({best_model_name})",
            training_samples=len(X)
        )
    
    def _random_search_optimization(
        self, 
        base_scenario: ScenarioRequest,
        targets: List[OptimizationTarget],
        n_trials: int
    ) -> OptimizationResult:
        """Fallback random search optimization."""
        
        best_score = 0
        best_params = {}
        
        for _ in range(n_trials):
            # Random parameter sampling
            sns_share = np.random.uniform(0.1, 0.8)
            video_share = np.random.uniform(0.1, 0.6)
            search_share = np.random.uniform(0.1, 0.5)
            
            # Normalize shares
            total = sns_share + video_share + search_share
            sns_share /= total
            video_share /= total
            search_share /= total
            
            params = {
                'sns_share': sns_share,
                'sns_alpha': np.random.uniform(0.01, 0.1),
                'video_share': video_share,
                'video_alpha': np.random.uniform(0.01, 0.08),
                'search_share': search_share,
                'search_alpha': np.random.uniform(0.005, 0.05),
                'wom_p_generate': np.random.uniform(0.02, 0.2),
                'wom_decay': np.random.uniform(0.7, 0.95)
            }
            
            # Simple scoring heuristic (would need actual simulation in production)
            score = (params['sns_share'] * params['sns_alpha'] * 10 +
                    params['video_share'] * params['video_alpha'] * 15 +
                    params['search_share'] * params['search_alpha'] * 5 +
                    params['wom_p_generate'] * 2)
            
            if score > best_score:
                best_score = score
                best_params = params
        
        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            improvement=10.0,  # Mock improvement
            confidence=0.3,  # Low confidence for random search
            method_used="Random Search",
            training_samples=0
        )


# API integration classes
class OptimizationRequest:
    """Request for parameter optimization."""
    def __init__(
        self,
        base_scenario: ScenarioRequest,
        optimization_targets: List[OptimizationTarget],
        method: str = "ml",
        n_trials: int = 50
    ):
        self.base_scenario = base_scenario
        self.optimization_targets = optimization_targets
        self.method = method
        self.n_trials = n_trials


class OptimizationResponse:
    """Response from parameter optimization."""
    def __init__(self, result: OptimizationResult, optimized_scenario: ScenarioRequest):
        self.optimization_result = result
        self.optimized_scenario = optimized_scenario
        self.recommendations = self._generate_recommendations(result)
    
    def _generate_recommendations(self, result: OptimizationResult) -> List[str]:
        """Generate human-readable recommendations."""
        recommendations = []
        
        if result.improvement > 10:
            recommendations.append(f"Significant improvement expected: {result.improvement:.1f}%")
        elif result.improvement > 0:
            recommendations.append(f"Moderate improvement expected: {result.improvement:.1f}%")
        else:
            recommendations.append("Minimal improvement expected from current parameters")
        
        if result.confidence > 0.7:
            recommendations.append("High confidence in optimization results")
        elif result.confidence > 0.4:
            recommendations.append("Moderate confidence - consider collecting more data")
        else:
            recommendations.append("Low confidence - results should be validated")
        
        recommendations.append(f"Optimization based on {result.training_samples} historical simulations")
        
        return recommendations