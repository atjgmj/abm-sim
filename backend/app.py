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
    RunStatus, NetworkConfig
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
                steps=scenario.steps,
                seed=rep_seed
            )
            
            print(f"Model created, running simulation...")
            
            # Run simulation
            results = model.run()
            all_results.append(results)
            print(f"Repetition {rep + 1} completed")
        
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)