"""Training data generator for ML optimization."""

import asyncio
import logging
import json
import uuid
from typing import Dict, Any, List
from dataclasses import dataclass
import numpy as np

from schemas import ScenarioRequest, MediaMix, MediaChannel, WordOfMouthConfig, NetworkConfig
from schemas import PersonalityConfig, DemographicConfig, InfluencerConfig, NetworkType
from model.abm import CommunicationModel
from store.db import SimulationStore

logger = logging.getLogger(__name__)


@dataclass
class TrainingDataStatus:
    """Status of training data collection."""
    total_simulations: int
    recommended_minimum: int = 50
    data_quality: str = "Poor"  # Poor, Limited, Good, Excellent
    suitable_for_training: bool = False
    last_generated: str = "Never"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_simulations": self.total_simulations,
            "recommended_minimum": self.recommended_minimum,
            "data_quality": self.data_quality,
            "suitable_for_training": self.suitable_for_training,
            "last_generated": self.last_generated
        }


class TrainingDataGenerator:
    """Generate diverse scenarios for ML training."""
    
    def __init__(self, store: SimulationStore):
        self.store = store
    
    def get_training_data_status(self) -> TrainingDataStatus:
        """Get current status of training data."""
        simulations = self.store.get_all_simulations()
        total_count = len(simulations)
        
        # Assess data quality
        if total_count >= 100:
            quality = "Excellent"
        elif total_count >= 50:
            quality = "Good"
        elif total_count >= 20:
            quality = "Limited"
        else:
            quality = "Poor"
        
        suitable = total_count >= 20
        
        return TrainingDataStatus(
            total_simulations=total_count,
            data_quality=quality,
            suitable_for_training=suitable
        )
    
    def generate_diverse_scenarios(self, base_scenario: ScenarioRequest, num_variants: int = 15) -> List[ScenarioRequest]:
        """Generate diverse scenario variants for training."""
        scenarios = []
        
        # Parameter ranges for variation
        param_ranges = {
            'sns_share': (0.2, 0.7),
            'sns_alpha': (0.01, 0.08),
            'video_share': (0.15, 0.5),
            'video_alpha': (0.01, 0.06),
            'search_share': (0.1, 0.4),
            'search_alpha': (0.005, 0.04),
            'wom_p_generate': (0.03, 0.15),
            'wom_decay': (0.75, 0.95),
            'personality_openness': (0.3, 0.8),
            'personality_social_influence': (0.2, 0.8),
            'influencer_ratio': (0.005, 0.04),
            'influence_multiplier': (1.5, 4.0),
            'network_k': (4, 15)
        }
        
        np.random.seed(42)
        
        for i in range(num_variants):
            # Create variant based on base scenario
            variant = base_scenario.model_copy(deep=True)
            variant.name = f"Training Variant {i+1}"
            
            # Randomly vary parameters
            sns_share = np.random.uniform(*param_ranges['sns_share'])
            video_share = np.random.uniform(*param_ranges['video_share'])
            search_share = np.random.uniform(*param_ranges['search_share'])
            
            # Normalize shares
            total_share = sns_share + video_share + search_share
            sns_share /= total_share
            video_share /= total_share
            search_share /= total_share
            
            # Apply variations
            variant.media_mix.sns.share = sns_share
            variant.media_mix.sns.alpha = np.random.uniform(*param_ranges['sns_alpha'])
            variant.media_mix.video.share = video_share
            variant.media_mix.video.alpha = np.random.uniform(*param_ranges['video_alpha'])
            variant.media_mix.search.share = search_share
            variant.media_mix.search.alpha = np.random.uniform(*param_ranges['search_alpha'])
            
            variant.wom.p_generate = np.random.uniform(*param_ranges['wom_p_generate'])
            variant.wom.decay = np.random.uniform(*param_ranges['wom_decay'])
            
            variant.personality.openness = np.random.uniform(*param_ranges['personality_openness'])
            variant.personality.social_influence = np.random.uniform(*param_ranges['personality_social_influence'])
            
            variant.influencers.influencer_ratio = np.random.uniform(*param_ranges['influencer_ratio'])
            variant.influencers.influence_multiplier = np.random.uniform(*param_ranges['influence_multiplier'])
            
            variant.network.k = int(np.random.uniform(*param_ranges['network_k']))
            
            # Randomly select network type
            variant.network.type = np.random.choice([
                "er",  # NetworkType.ERDOS_RENYI
                "ws",  # NetworkType.WATTS_STROGATZ
                "ba"   # NetworkType.BARABASI_ALBERT
            ])
            
            # Reduce simulation size for faster training data generation
            variant.network.n = min(1000, variant.network.n)
            variant.steps = min(30, variant.steps)
            variant.reps = min(3, variant.reps)
            
            scenarios.append(variant)
        
        return scenarios
    
    async def run_simulation_batch(self, scenarios: List[ScenarioRequest]) -> Dict[str, Any]:
        """Run a batch of simulations for training data."""
        results = {"completed": 0, "failed": 0, "details": []}
        
        for i, scenario in enumerate(scenarios):
            try:
                logger.info(f"Running training simulation {i+1}/{len(scenarios)}")
                
                # Create scenario in store
                scenario_id = self.store.save_scenario(scenario)
                
                # Run simulation
                from model.network import generate_network
                network = generate_network(
                    scenario.network.type,
                    scenario.network.n,
                    scenario.network.k,
                    scenario.network.beta or 0.1,
                    scenario.seed
                )
                
                model = CommunicationModel(
                    network=network,
                    media_mix=scenario.media_mix,
                    wom_config=scenario.wom,
                    personality_config=scenario.personality,
                    demographic_config=scenario.demographics,
                    influencer_config=scenario.influencers,
                    steps=scenario.steps,
                    seed=scenario.seed
                )
                
                # Run simulation for specified steps
                for step in range(scenario.steps):
                    model.step()
                
                # Collect final results
                simulation_results = {
                    "summary": {},
                    "time_series": []
                }
                
                # Get final counts for each KPI
                for kpi in ['awareness', 'interest', 'knowledge', 'liking', 'intent']:
                    final_count = getattr(model.datacollector.model_vars, f'final_{kpi}', [0])[-1] if hasattr(model.datacollector.model_vars, f'final_{kpi}') else 0
                    simulation_results["summary"][kpi] = {
                        "start": 0,
                        "end": final_count,
                        "change": final_count
                    }
                
                # Store results
                run_id = str(uuid.uuid4())
                self.store.save_results(run_id, {
                    "scenario_id": scenario_id,
                    "scenario": scenario.model_dump(),
                    "results": simulation_results
                })
                
                results["completed"] += 1
                results["details"].append({
                    "scenario_id": scenario_id,
                    "run_id": run_id,
                    "status": "completed"
                })
                
                logger.info(f"Completed training simulation {i+1}")
                
            except Exception as e:
                logger.error(f"Failed training simulation {i+1}: {e}")
                results["failed"] += 1
                results["details"].append({
                    "scenario_id": scenario_id if 'scenario_id' in locals() else None,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    async def generate_training_data(self, base_scenario: ScenarioRequest, num_variants: int = 15) -> Dict[str, Any]:
        """Generate comprehensive training data."""
        logger.info(f"Starting training data generation with {num_variants} variants")
        
        # Generate diverse scenarios
        scenarios = self.generate_diverse_scenarios(base_scenario, num_variants)
        
        # Run simulations
        results = await self.run_simulation_batch(scenarios)
        
        # Update status
        status = self.get_training_data_status()
        
        return {
            "message": f"Generated {results['completed']} training simulations",
            "batch_results": results,
            "training_status": status.to_dict(),
            "estimated_completion": f"{results['completed'] * 30} seconds"
        }


# Utility functions for API integration
def calculate_estimated_time(num_variants: int, network_size: int = 1000) -> str:
    """Calculate estimated completion time."""
    # Rough estimates based on simulation complexity
    time_per_sim = max(10, network_size / 100)  # seconds
    total_time = num_variants * time_per_sim
    
    if total_time < 60:
        return f"{int(total_time)} seconds"
    elif total_time < 3600:
        return f"{int(total_time / 60)} minutes"
    else:
        return f"{int(total_time / 3600)} hours {int((total_time % 3600) / 60)} minutes"


def get_training_recommendations(current_count: int) -> List[str]:
    """Get recommendations for improving training data."""
    recommendations = []
    
    if current_count < 20:
        recommendations.append("Generate at least 20 simulations for basic ML training")
        recommendations.append("Consider using smaller network sizes (1000 nodes) for faster generation")
    elif current_count < 50:
        recommendations.append("Generate 50+ simulations for reliable optimization")
        recommendations.append("Include diverse parameter combinations")
    elif current_count < 100:
        recommendations.append("Consider expanding to 100+ simulations for advanced optimization")
        recommendations.append("Add scenarios with different network types")
    else:
        recommendations.append("Excellent training data coverage")
        recommendations.append("ML optimization should be highly reliable")
    
    return recommendations