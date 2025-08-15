"""FastAPI backend for ABM Communication Campaign Simulator."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .schemas import (
    ScenarioRequest, ScenarioResponse, RunRequest, RunResponse,
    RunStatusResponse, ResultsResponse, NetworkPreviewResponse,
    RunStatus, NetworkConfig, KPICategory
)
from .external.social_media import (
    ParameterCalibrator, ExternalDataRequest, CalibratedParametersResponse
)
from .external.competitor_analysis import CompetitorAnalyzer, IndustryType
from .external.roi_optimizer import ROIOptimizer
from .ml.optimizer import (
    ParameterOptimizer, OptimizationTarget, OptimizationRequest, OptimizationResponse
)
from .model.network import generate_network, network_to_preview
from .model.abm import CommunicationModel
from .store.db import SimulationStore

# Global state
store = SimulationStore()
executor = ThreadPoolExecutor(max_workers=2)  # Limit concurrent simulations
running_simulations: Dict[str, asyncio.Task] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    yield
    # Cleanup
    executor.shutdown(wait=True)


app = FastAPI(
    title="ABM Communication Campaign Simulator",
    description="Agent-Based Model for simulating communication campaign effectiveness",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "ABM Communication Campaign Simulator API"}


@app.post("/api/scenario", response_model=ScenarioResponse)
async def create_scenario(scenario: ScenarioRequest) -> ScenarioResponse:
    """Create a new simulation scenario."""
    try:
        scenario_id = store.save_scenario(scenario)
        return ScenarioResponse(id=scenario_id, scenario=scenario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create scenario: {str(e)}")


@app.get("/api/scenarios")
async def list_scenarios():
    """List all scenarios."""
    return store.list_scenarios()


@app.post("/api/run", response_model=RunResponse)
async def create_run(request: RunRequest, background_tasks: BackgroundTasks) -> RunResponse:
    """Start a new simulation run."""
    scenario = store.get_scenario(request.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    run_id = store.create_run(request.scenario_id)
    print(f"Created run {run_id}, starting background task")
    
    # Start background simulation
    background_tasks.add_task(run_simulation, run_id, scenario)
    print(f"Background task added for run {run_id}")
    
    return RunResponse(run_id=run_id)


@app.get("/api/run/{run_id}/status", response_model=RunStatusResponse)
async def get_run_status(run_id: str) -> RunStatusResponse:
    """Get simulation run status."""
    try:
        status_info = store.get_run_status(run_id)
        if not status_info:
            raise HTTPException(status_code=404, detail="Run not found")
        
        return RunStatusResponse(**status_info)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting run status for {run_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get run status: {str(e)}")


@app.get("/api/run/{run_id}/results")
async def get_run_results(run_id: str, agg: str = "day") -> ResultsResponse:
    """Get simulation results."""
    results = store.get_results(run_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    # For now, ignore agg parameter and return raw results
    return ResultsResponse(
        run_id=run_id,
        series=results['series'],
        summary=results['summary']
    )


@app.get("/api/run/{run_id}/export/csv")
async def export_results_csv(run_id: str):
    """Export results as CSV."""
    csv_path = store.export_results_csv(run_id)
    if not csv_path:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return FileResponse(csv_path, filename=f"simulation_{run_id}.csv")


@app.get("/api/run/{run_id}/test")
async def test_run_status(run_id: str):
    """Test endpoint to debug run status issues."""
    try:
        print(f"Testing run status for {run_id}")
        
        # Check if run exists in database
        import sqlite3
        conn = sqlite3.connect('data/simulation.db')
        cursor = conn.execute('SELECT * FROM runs WHERE id = ?', (run_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "run_id": run_id,
                "found": True,
                "status": row[2],
                "progress": row[3],
                "message": row[4],
                "raw_row": row
            }
        else:
            return {
                "run_id": run_id,
                "found": False
            }
    except Exception as e:
        print(f"Test endpoint error: {str(e)}")
        return {"error": str(e)}


@app.post("/api/network/preview", response_model=NetworkPreviewResponse)
async def preview_network(config: NetworkConfig) -> NetworkPreviewResponse:
    """Generate network preview."""
    try:
        # Limit preview size for performance
        preview_n = min(config.n, 1000)
        
        network = generate_network(
            config.type,
            preview_n,
            config.k,
            config.beta or 0.1,
            42  # Fixed seed for consistent previews
        )
        
        nodes, edges = network_to_preview(network, max_nodes=500)
        
        return NetworkPreviewResponse(nodes=nodes, edges=edges)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")


async def run_simulation(run_id: str, scenario: ScenarioRequest) -> None:
    """Run simulation in background."""
    import traceback
    
    try:
        print(f"Starting simulation {run_id}")
        
        # Update status to running
        store.update_run_status(run_id, RunStatus.RUNNING, 0.1, "Generating network...")
        
        # Generate network
        print(f"Generating network: {scenario.network.type}, n={scenario.network.n}")
        network = generate_network(
            scenario.network.type,
            scenario.network.n,
            scenario.network.k,
            scenario.network.beta or 0.1,
            scenario.seed
        )
        print(f"Network generated with {network.number_of_nodes()} nodes")
        
        store.update_run_status(run_id, RunStatus.RUNNING, 0.2, "Initializing model...")
        
        # Run multiple repetitions
        all_results = []
        
        for rep in range(scenario.reps):
            progress = 0.2 + (rep / scenario.reps) * 0.7
            store.update_run_status(
                run_id, 
                RunStatus.RUNNING, 
                progress, 
                f"Running repetition {rep + 1}/{scenario.reps}..."
            )
            
            print(f"Running repetition {rep + 1}/{scenario.reps}")
            
            # Create model with different seed for each repetition
            rep_seed = scenario.seed + rep if scenario.seed else None
            print(f"Creating model with seed {rep_seed}")
            
            model = CommunicationModel(
                network=network,
                media_mix=scenario.media_mix,
                wom_config=scenario.wom,
                personality_config=scenario.personality,
                demographic_config=scenario.demographics,
                influencer_config=scenario.influencers,
                steps=scenario.steps,
                seed=rep_seed
            )
            
            print(f"Model created, running simulation...")
            
            # Run simulation with timeout (5 minutes per repetition)
            try:
                loop = asyncio.get_event_loop()
                results = await asyncio.wait_for(
                    loop.run_in_executor(executor, model.run),
                    timeout=300  # 5 minute timeout per repetition
                )
                all_results.append(results)
                print(f"Repetition {rep + 1} completed")
            except asyncio.TimeoutError:
                raise Exception(f"Simulation repetition {rep + 1} timed out after 5 minutes")
        
        store.update_run_status(run_id, RunStatus.RUNNING, 0.95, "Aggregating results...")
        
        # Aggregate results across repetitions
        aggregated_results = aggregate_repetitions(all_results)
        
        # Save results
        store.save_results(run_id, aggregated_results)
        
        # Mark as completed
        store.update_run_status(run_id, RunStatus.DONE, 1.0, "Completed successfully")
        print(f"Simulation {run_id} completed successfully")
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"Simulation {run_id} failed: {error_msg}")
        print("Traceback:")
        traceback.print_exc()
        store.update_run_status(run_id, RunStatus.ERROR, 0.0, error_msg)


def aggregate_repetitions(results_list) -> Dict[str, Any]:
    """Aggregate results across multiple repetitions."""
    if not results_list:
        return {}
    
    # For now, just return the first repetition's results
    # In a full implementation, you'd average across repetitions
    return results_list[0]


@app.post("/api/calibrate", response_model=CalibratedParametersResponse)
async def calibrate_parameters(request: ExternalDataRequest):
    """Calibrate ABM parameters using external social media data."""
    try:
        calibrator = ParameterCalibrator()
        
        calibrated_params = await calibrator.calibrate_from_campaign_data(
            request.campaign_keywords,
            request.baseline_scenario
        )
        
        # Calculate confidence score based on data availability
        confidence_score = 0.75  # Mock confidence for synthetic data
        
        calibration_notes = [
            "Parameters calibrated using social media engagement data",
            "Media mix adjusted based on platform performance",
            "Demographics calibrated from audience insights",
            "Personality traits derived from engagement patterns"
        ]
        
        if not request.api_keys:
            calibration_notes.append("Using synthetic data - provide API keys for real data")
            confidence_score = 0.5
        
        return CalibratedParametersResponse(
            original_params=request.baseline_scenario,
            calibrated_params=calibrated_params,
            data_sources=["twitter", "instagram", "tiktok"],
            confidence_score=confidence_score,
            calibration_notes=calibration_notes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calibration failed: {str(e)}")


@app.get("/api/trending")
async def get_trending_topics(limit: int = 10):
    """Get current trending topics for campaign keyword suggestions."""
    try:
        from .external.social_media import SocialMediaAnalyzer
        
        async with SocialMediaAnalyzer() as analyzer:
            trends = await analyzer.get_trending_topics(limit)
        
        return {
            "trends": [
                {
                    "keyword": trend.keyword,
                    "volume": trend.volume,
                    "sentiment": trend.sentiment,
                    "growth_rate": trend.growth_rate
                }
                for trend in trends
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")


@app.post("/api/optimize")
async def optimize_parameters(request: dict):
    """Optimize ABM parameters using machine learning."""
    try:
        # Parse request - fix data types to match schema expectations
        scenario_data = request['base_scenario']
        
        # Fix network type mapping
        if 'network' in scenario_data and 'type' in scenario_data['network']:
            network_type = scenario_data['network']['type']
            type_mapping = {
                'erdos_renyi': 'er',
                'watts_strogatz': 'ws', 
                'barabasi_albert': 'ba',
                'er': 'er',
                'ws': 'ws',
                'ba': 'ba'
            }
            scenario_data['network']['type'] = type_mapping.get(network_type, 'ws')
        
        # Fix demographics - ensure integers
        if 'demographics' in scenario_data:
            demo = scenario_data['demographics']
            if 'age_group' in demo:
                demo['age_group'] = int(round(demo['age_group'])) if isinstance(demo['age_group'], (int, float)) else 3
                demo['age_group'] = max(1, min(5, demo['age_group']))
            if 'income_level' in demo:
                demo['income_level'] = int(round(demo['income_level'])) if isinstance(demo['income_level'], (int, float)) else 3
                demo['income_level'] = max(1, min(5, demo['income_level']))
            if 'education_level' in demo:
                demo['education_level'] = int(round(demo['education_level'])) if isinstance(demo['education_level'], (int, float)) else 3
                demo['education_level'] = max(1, min(5, demo['education_level']))
        
        base_scenario = ScenarioRequest(**scenario_data)
        
        # Create optimization targets
        targets = []
        for target_data in request.get('optimization_targets', []):
            targets.append(OptimizationTarget(
                kpi=KPICategory(target_data['kpi']),
                target_value=target_data['target_value'],
                weight=target_data.get('weight', 1.0),
                target_type=target_data.get('target_type', 'maximize')
            ))
        
        if not targets:
            # Default targets
            targets = [
                OptimizationTarget(kpi=KPICategory.AWARENESS, target_value=5000, weight=0.6),
                OptimizationTarget(kpi=KPICategory.INTENT, target_value=1000, weight=0.4)
            ]
        
        # Initialize optimizer
        optimizer = ParameterOptimizer(store)
        
        # Run optimization
        result = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: optimizer.optimize_parameters_ml(
                base_scenario,
                targets,
                request.get('n_trials', 30)
            )
        )
        
        # Create optimized scenario
        optimized_scenario = base_scenario.model_copy(deep=True)
        
        # Apply optimized parameters
        if 'sns_share' in result.best_params:
            optimized_scenario.media_mix.sns.share = result.best_params['sns_share']
            optimized_scenario.media_mix.sns.alpha = result.best_params['sns_alpha']
            optimized_scenario.media_mix.video.share = result.best_params['video_share']
            optimized_scenario.media_mix.video.alpha = result.best_params['video_alpha']
            optimized_scenario.media_mix.search.share = result.best_params['search_share']
            optimized_scenario.media_mix.search.alpha = result.best_params['search_alpha']
            
            optimized_scenario.wom.p_generate = result.best_params['wom_p_generate']
            optimized_scenario.wom.decay = result.best_params['wom_decay']
            
            if 'personality_openness' in result.best_params:
                optimized_scenario.personality.openness = result.best_params['personality_openness']
                optimized_scenario.personality.social_influence = result.best_params['personality_social_influence']
                optimized_scenario.personality.media_affinity = result.best_params['personality_media_affinity']
                optimized_scenario.personality.risk_tolerance = result.best_params['personality_risk_tolerance']
            
            if 'influencers_enabled' in result.best_params:
                optimized_scenario.influencers.enable_influencers = result.best_params['influencers_enabled']
                optimized_scenario.influencers.influencer_ratio = result.best_params['influencers_ratio']
                optimized_scenario.influencers.influence_multiplier = result.best_params['influencers_multiplier']
        
        # Generate recommendations
        recommendations = []
        if result.improvement > 10:
            recommendations.append(f"Significant improvement expected: {result.improvement:.1f}%")
        elif result.improvement > 0:
            recommendations.append(f"Moderate improvement expected: {result.improvement:.1f}%")
        else:
            recommendations.append("Current parameters appear near-optimal")
        
        if result.confidence > 0.7:
            recommendations.append("High confidence in optimization results")
        elif result.confidence > 0.4:
            recommendations.append("Moderate confidence - recommend validation")
        else:
            recommendations.append("Low confidence - collect more training data")
        
        return {
            "optimization_result": {
                "best_params": result.best_params,
                "best_score": result.best_score,
                "improvement": result.improvement,
                "confidence": result.confidence,
                "method_used": result.method_used,
                "training_samples": result.training_samples
            },
            "optimized_scenario": optimized_scenario.model_dump(),
            "recommendations": recommendations
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/api/training-data-status")
async def get_training_data_status():
    """Get status of available training data for ML optimization."""
    try:
        optimizer = ParameterOptimizer(store)
        simulations = store.get_all_simulations()
        
        return {
            "total_simulations": len(simulations),
            "suitable_for_training": len(simulations) >= 10,
            "recommended_minimum": 20,
            "data_quality": "Good" if len(simulations) >= 20 else "Limited" if len(simulations) >= 10 else "Insufficient"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get training data status: {str(e)}")


@app.post("/api/generate-training-data")
async def generate_training_data(request: dict, background_tasks: BackgroundTasks):
    """Generate training data by running multiple simulation variants."""
    try:
        base_scenario = ScenarioRequest(**request.get('base_scenario', {}))
        num_variants = request.get('num_variants', 15)
        
        # Generate parameter variants
        variants = []
        import random
        random.seed(42)
        
        for i in range(num_variants):
            variant = base_scenario.model_copy(deep=True)
            
            # Vary media mix
            sns_share = random.uniform(0.2, 0.6)
            video_share = random.uniform(0.2, 0.5)
            search_share = random.uniform(0.1, 0.4)
            
            # Normalize shares
            total = sns_share + video_share + search_share
            variant.media_mix.sns.share = sns_share / total
            variant.media_mix.video.share = video_share / total
            variant.media_mix.search.share = search_share / total
            
            # Vary alphas
            variant.media_mix.sns.alpha = random.uniform(0.02, 0.08)
            variant.media_mix.video.alpha = random.uniform(0.01, 0.05)
            variant.media_mix.search.alpha = random.uniform(0.005, 0.03)
            
            # Vary WoM parameters
            variant.wom.p_generate = random.uniform(0.05, 0.15)
            variant.wom.decay = random.uniform(0.8, 0.95)
            variant.wom.personality_weight = random.uniform(0.2, 0.5)
            variant.wom.demographic_weight = random.uniform(0.1, 0.4)
            
            # Vary personality
            variant.personality.openness = random.uniform(0.3, 0.7)
            variant.personality.social_influence = random.uniform(0.3, 0.7)
            variant.personality.media_affinity = random.uniform(0.3, 0.7)
            variant.personality.risk_tolerance = random.uniform(0.3, 0.7)
            
            # Vary influencers
            variant.influencers.enable_influencers = random.choice([True, False])
            variant.influencers.influencer_ratio = random.uniform(0.01, 0.04)
            variant.influencers.influence_multiplier = random.uniform(2.0, 4.0)
            
            # Vary network size
            variant.network.n = random.choice([5000, 8000, 10000, 12000])
            variant.network.k = random.choice([4, 6, 8, 10])
            
            # Set unique name
            variant.name = f"Training_Variant_{i+1}"
            variant.seed = 42 + i
            
            variants.append(variant)
        
        # Save scenarios and queue runs
        variant_runs = []
        for variant in variants:
            scenario_id = store.save_scenario(variant)
            run_id = store.create_run(scenario_id)
            
            # Start background simulation
            background_tasks.add_task(run_simulation, run_id, variant)
            variant_runs.append({"scenario_id": scenario_id, "run_id": run_id})
        
        return {
            "message": f"Started {num_variants} training simulations",
            "variants": variant_runs,
            "estimated_completion": f"{num_variants * 2} minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate training data: {str(e)}")


@app.post("/api/competitor-analysis")
async def analyze_competitors(request: dict):
    """競合分析を実行"""
    try:
        industry = request.get('industry', 'technology')
        keywords = request.get('keywords', [])
        
        analyzer = CompetitorAnalyzer()
        analysis = await analyzer.analyze_competitors(
            IndustryType(industry), 
            keywords
        )
        
        return {
            "analysis": {
                "target_company": analysis.target_company,
                "industry": analysis.industry.value,
                "market_position": analysis.market_position,
                "competitors": [
                    {
                        "company": comp.company,
                        "awareness_rate": comp.awareness_rate,
                        "market_share": comp.market_share,
                        "social_engagement": comp.social_engagement,
                        "media_spend": comp.media_spend,
                        "conversion_rate": comp.conversion_rate
                    }
                    for comp in analysis.competitors
                ],
                "strengths": analysis.strengths,
                "opportunities": analysis.opportunities,
                "threats": analysis.threats,
                "recommended_strategies": analysis.recommended_strategies
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Competitor analysis failed: {str(e)}")


@app.get("/api/industry-insights/{industry}")
async def get_industry_insights(industry: str):
    """業界インサイトを取得"""
    try:
        analyzer = CompetitorAnalyzer()
        insights = await analyzer.get_industry_insights(IndustryType(industry))
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get industry insights: {str(e)}")


@app.post("/api/roi-prediction")
async def predict_roi(request: dict):
    """ROI予測と予算最適化"""
    try:
        media_mix = request.get('media_mix', {})
        total_budget = request.get('total_budget', 100000)
        historical_performance = request.get('historical_performance')
        
        optimizer = ROIOptimizer()
        prediction = await optimizer.predict_roi(
            media_mix, 
            total_budget, 
            historical_performance
        )
        
        return {
            "roi_prediction": {
                "scenario_name": prediction.scenario_name,
                "total_budget": prediction.total_budget,
                "predicted_revenue": prediction.predicted_revenue,
                "predicted_roi": prediction.predicted_roi,
                "confidence_interval": prediction.confidence_interval,
                "channel_breakdown": [
                    {
                        "channel": alloc.channel,
                        "current_budget": alloc.current_budget,
                        "optimal_budget": alloc.optimal_budget,
                        "expected_roi": alloc.expected_roi,
                        "confidence": alloc.confidence
                    }
                    for alloc in prediction.channel_breakdown
                ],
                "optimization_notes": prediction.optimization_notes
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ROI prediction failed: {str(e)}")


@app.post("/api/ab-test-scenarios")
async def generate_ab_test_scenarios(request: dict):
    """A/Bテストシナリオを自動生成"""
    try:
        base_scenario = request.get('base_scenario', {})
        total_budget = request.get('total_budget', 100000)
        test_variants = request.get('test_variants', 3)
        
        optimizer = ROIOptimizer()
        scenarios = await optimizer.generate_ab_test_scenarios(
            base_scenario,
            total_budget,
            test_variants
        )
        
        return {"test_scenarios": scenarios}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"A/B test scenario generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)