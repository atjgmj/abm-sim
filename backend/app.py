"""FastAPI backend for ABM Communication Campaign Simulator."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from schemas import (
    ScenarioRequest, ScenarioResponse, RunRequest, RunResponse,
    RunStatusResponse, ResultsResponse, NetworkPreviewResponse,
    RunStatus, NetworkConfig, KPICategory, MediaMix, MediaChannel,
    WordOfMouthConfig, PersonalityConfig, DemographicConfig, InfluencerConfig
)
from external.social_media import (
    ParameterCalibrator, ExternalDataRequest, CalibratedParametersResponse
)
from external.competitor_analysis import CompetitorAnalyzer, IndustryType
from external.roi_optimizer import ROIOptimizer
from external.data_sources import external_data_manager, DataSourceType, DataSourceStatus
from ml.optimizer import (
    ParameterOptimizer, OptimizationTarget, OptimizationRequest, OptimizationResponse
)
from ml.training_generator import TrainingDataGenerator
from model.network import generate_network, network_to_preview
from model.abm import CommunicationModel
from store.db import SimulationStore

# Global state
store = SimulationStore()
executor = ThreadPoolExecutor(max_workers=2)  # Limit concurrent simulations
running_simulations: Dict[str, asyncio.Task] = {}
optimizer = ParameterOptimizer(store)
training_generator = TrainingDataGenerator(store)


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
        from external.social_media import SocialMediaAnalyzer
        
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
        status = training_generator.get_training_data_status()
        return status.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get training data status: {str(e)}")


@app.post("/api/generate-training-data")
async def generate_training_data(request: dict, background_tasks: BackgroundTasks):
    """Generate training data by running multiple simulation variants."""
    try:
        base_scenario = ScenarioRequest(**request.get('base_scenario', {}))
        num_variants = request.get('num_variants', 15)
        
        # Use the training generator
        async def run_training_generation():
            return await training_generator.generate_training_data(base_scenario, num_variants)
        
        # Run in background
        background_tasks.add_task(run_training_generation)
        
        from ml.training_generator import calculate_estimated_time
        estimated_time = calculate_estimated_time(num_variants, base_scenario.network.n)
        
        return {
            "message": f"Training data generation started with {num_variants} variants",
            "estimated_completion": estimated_time,
            "status": "generating"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate training data: {str(e)}")


@app.post("/api/auto-generate-training-data")
async def auto_generate_training_data(background_tasks: BackgroundTasks):
    """Automatically generate training data if insufficient."""
    try:
        # Check current status
        status = training_generator.get_training_data_status()
        
        if status.total_simulations >= 50:
            return {
                "message": "Sufficient training data already exists",
                "current_count": status.total_simulations,
                "status": "sufficient"
            }
        
        # Create a default base scenario for training
        default_base_scenario = ScenarioRequest(
            name="Auto Training Base",
            description="Automatically generated base scenario for training",
            network=NetworkConfig(
                type="ws",
                n=1000,  # Smaller for faster generation
                k=6,
                beta=0.1
            ),
            media_mix=MediaMix(
                sns=MediaChannel(share=0.4, alpha=0.05),
                video=MediaChannel(share=0.35, alpha=0.04),
                search=MediaChannel(share=0.25, alpha=0.02)
            ),
            wom=WordOfMouthConfig(
                p_generate=0.08,
                decay=0.85
            ),
            personality=PersonalityConfig(
                openness=0.6,
                social_influence=0.5,
                media_affinity=0.5,
                risk_tolerance=0.4
            ),
            demographics=DemographicConfig(
                age_group=3,
                income_level=3,
                urban_rural=0.7,
                education_level=3
            ),
            influencers=InfluencerConfig(
                enable_influencers=True,
                influencer_ratio=0.02,
                influence_multiplier=2.5
            ),
            steps=30,  # Shorter for faster generation
            reps=3,    # Fewer repetitions
            seed=42
        )
        
        # Calculate how many variants we need
        needed_variants = max(20, 50 - status.total_simulations)
        
        # Generate training data in background
        async def run_auto_training():
            return await training_generator.generate_training_data(default_base_scenario, needed_variants)
        
        background_tasks.add_task(run_auto_training)
        
        from ml.training_generator import calculate_estimated_time
        estimated_time = calculate_estimated_time(needed_variants, 1000)
        
        return {
            "message": f"Auto-generating {needed_variants} training variants",
            "current_count": status.total_simulations,
            "target_count": status.total_simulations + needed_variants,
            "estimated_completion": estimated_time,
            "status": "generating"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto-generate training data: {str(e)}")


@app.get("/api/training-recommendations")
async def get_training_recommendations():
    """Get recommendations for improving training data."""
    try:
        status = training_generator.get_training_data_status()
        
        from ml.training_generator import get_training_recommendations
        recommendations = get_training_recommendations(status.total_simulations)
        
        return {
            "current_status": status.to_dict(),
            "recommendations": recommendations,
            "auto_generate_available": status.total_simulations < 50
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@app.get("/api/demo-data-status")
async def get_demo_data_status():
    """Get status of demo data availability."""
    try:
        from demo_data.loader import demo_loader
        status = demo_loader.get_data_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get demo data status: {str(e)}")


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


# External Data Management Endpoints

@app.get("/api/external-data/sources")
async def get_external_data_sources():
    """外部データソース一覧を取得"""
    try:
        async with external_data_manager as manager:
            statuses = await manager.get_all_statuses()
        
        return {
            "data_sources": [
                {
                    "type": status.source_type.value,
                    "status": status.status,
                    "last_sync": status.last_sync.isoformat() if status.last_sync else None,
                    "error_message": status.error_message,
                    "records_count": status.records_count
                }
                for status in statuses
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data sources: {str(e)}")


@app.post("/api/external-data/config")
async def update_external_data_config(request: dict):
    """外部データソース設定を更新"""
    try:
        source_type = DataSourceType(request.get('source_type'))
        config_updates = request.get('config', {})
        
        external_data_manager.update_api_config(source_type, **config_updates)
        
        return {
            "message": f"Configuration updated for {source_type.value}",
            "source_type": source_type.value,
            "updated_fields": list(config_updates.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@app.post("/api/external-data/test-connection")
async def test_external_connection(request: dict):
    """外部データソース接続テスト"""
    try:
        source_type = DataSourceType(request.get('source_type'))
        
        async with external_data_manager as manager:
            status = await manager.test_connection(source_type)
        
        return {
            "source_type": status.source_type.value,
            "status": status.status,
            "error_message": status.error_message,
            "last_sync": status.last_sync.isoformat() if status.last_sync else None,
            "records_count": status.records_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")


@app.post("/api/external-data/upload")
async def upload_external_file(
    file: UploadFile = File(...),
    data_mapping: str = Form(None)
):
    """外部データファイルをアップロード"""
    try:
        # ファイルデータを読み取り
        file_content = await file.read()
        
        # ファイルをアップロード
        upload_result = external_data_manager.upload_file(
            file_content, 
            file.filename,
            file.content_type
        )
        
        if not upload_result.get('success'):
            raise HTTPException(status_code=400, detail=upload_result.get('error'))
        
        # データマッピングが提供された場合は適用
        if data_mapping:
            try:
                import json
                mapping_dict = json.loads(data_mapping)
                load_result = external_data_manager.load_file_data(
                    upload_result['file_path'],
                    mapping_dict
                )
                upload_result['data_preview'] = load_result
            except json.JSONDecodeError:
                upload_result['mapping_error'] = "Invalid data mapping JSON"
        
        return {
            "upload_result": upload_result,
            "file_info": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(file_content)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.post("/api/external-data/load-file")
async def load_external_file_data(request: dict):
    """アップロードされたファイルからデータを読み込み"""
    try:
        file_path = request.get('file_path')
        data_mapping = request.get('data_mapping', {})
        
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path is required")
        
        load_result = external_data_manager.load_file_data(file_path, data_mapping)
        
        if not load_result.get('success'):
            raise HTTPException(status_code=400, detail=load_result.get('error'))
        
        return load_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File data loading failed: {str(e)}")


@app.get("/api/external-data/status")
async def get_external_data_status():
    """外部データ連携の全体状況を取得"""
    try:
        async with external_data_manager as manager:
            statuses = await manager.get_all_statuses()
        
        # 統計情報を計算
        total_sources = len(statuses)
        connected_sources = len([s for s in statuses if s.status == "connected"])
        error_sources = len([s for s in statuses if s.status == "error"])
        disabled_sources = len([s for s in statuses if s.status == "disabled"])
        
        # 最新データの情報
        latest_sync = None
        total_records = 0
        
        for status in statuses:
            if status.last_sync:
                if not latest_sync or status.last_sync > latest_sync:
                    latest_sync = status.last_sync
            total_records += status.records_count
        
        return {
            "summary": {
                "total_sources": total_sources,
                "connected_sources": connected_sources,
                "error_sources": error_sources,
                "disabled_sources": disabled_sources,
                "connection_rate": connected_sources / total_sources if total_sources > 0 else 0,
                "latest_sync": latest_sync.isoformat() if latest_sync else None,
                "total_records": total_records
            },
            "sources": [
                {
                    "type": status.source_type.value,
                    "status": status.status,
                    "last_sync": status.last_sync.isoformat() if status.last_sync else None,
                    "error_message": status.error_message,
                    "records_count": status.records_count,
                    "data_freshness": status.data_freshness.isoformat() if status.data_freshness else None
                }
                for status in statuses
            ],
            "recommendations": _get_data_source_recommendations(statuses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get external data status: {str(e)}")


def _get_data_source_recommendations(statuses: list) -> list:
    """データソースの推奨事項を生成"""
    recommendations = []
    
    error_sources = [s for s in statuses if s.status == "error"]
    if error_sources:
        recommendations.append(f"{len(error_sources)}個のデータソースでエラーが発生しています。設定を確認してください。")
    
    disabled_sources = [s for s in statuses if s.status == "disabled"]
    if disabled_sources:
        recommendations.append(f"{len(disabled_sources)}個のデータソースが無効になっています。有効化を検討してください。")
    
    connected_sources = [s for s in statuses if s.status == "connected"]
    if len(connected_sources) < 2:
        recommendations.append("より多くのデータソースを接続することで、分析精度が向上します。")
    
    # データの新鮮さをチェック
    from datetime import datetime, timedelta
    stale_threshold = datetime.now() - timedelta(days=7)
    stale_sources = [s for s in connected_sources if s.last_sync and s.last_sync < stale_threshold]
    
    if stale_sources:
        recommendations.append(f"{len(stale_sources)}個のデータソースが1週間以上更新されていません。")
    
    if not recommendations:
        recommendations.append("データソースの設定は良好です。")
    
    return recommendations


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)