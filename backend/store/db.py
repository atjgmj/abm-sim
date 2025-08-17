"""Database and storage utilities."""

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd

from schemas import ScenarioRequest, RunStatus


class SimulationStore:
    """Store for simulation scenarios and results."""
    
    def __init__(self, db_path: str = "data/simulation.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scenarios (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    config TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    progress REAL DEFAULT 0.0,
                    message TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    results_path TEXT,
                    FOREIGN KEY (scenario_id) REFERENCES scenarios (id)
                )
            """)
            
            conn.commit()
    
    def save_scenario(self, scenario: ScenarioRequest) -> str:
        """Save scenario and return ID."""
        scenario_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO scenarios (id, name, config) VALUES (?, ?, ?)",
                (scenario_id, scenario.name, scenario.model_dump_json())
            )
            conn.commit()
        
        return scenario_id
    
    def get_scenario(self, scenario_id: str) -> Optional[ScenarioRequest]:
        """Retrieve scenario by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT config FROM scenarios WHERE id = ?",
                (scenario_id,)
            )
            row = cursor.fetchone()
        
        if row:
            return ScenarioRequest.model_validate_json(row[0])
        return None
    
    def list_scenarios(self) -> List[Dict[str, Any]]:
        """List all scenarios."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, name, created_at FROM scenarios ORDER BY created_at DESC"
            )
            return [
                {"id": row[0], "name": row[1], "created_at": row[2]}
                for row in cursor.fetchall()
            ]
    
    def create_run(self, scenario_id: str) -> str:
        """Create new run and return ID."""
        run_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO runs (id, scenario_id, status, started_at) VALUES (?, ?, ?, ?)",
                (run_id, scenario_id, RunStatus.QUEUED, datetime.now())
            )
            conn.commit()
        
        return run_id
    
    def update_run_status(
        self,
        run_id: str,
        status: RunStatus,
        progress: float = 0.0,
        message: Optional[str] = None
    ) -> None:
        """Update run status."""
        with sqlite3.connect(self.db_path) as conn:
            if status == RunStatus.DONE:
                conn.execute(
                    """UPDATE runs 
                       SET status = ?, progress = ?, message = ?, completed_at = ?
                       WHERE id = ?""",
                    (status, progress, message, datetime.now(), run_id)
                )
            else:
                conn.execute(
                    "UPDATE runs SET status = ?, progress = ?, message = ? WHERE id = ?",
                    (status, progress, message, run_id)
                )
            conn.commit()
    
    def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT status, progress, message FROM runs WHERE id = ?",
                (run_id,)
            )
            row = cursor.fetchone()
        
        if row:
            return {
                "status": RunStatus(row[0]),
                "progress": row[1],
                "message": row[2]
            }
        return None
    
    def save_results(self, run_id: str, results: Dict[str, Any]) -> str:
        """Save simulation results."""
        results_dir = Path("data/results")
        results_dir.mkdir(exist_ok=True)
        
        results_path = results_dir / f"{run_id}.json"
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Update run record
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE runs SET results_path = ? WHERE id = ?",
                (str(results_path), run_id)
            )
            conn.commit()
        
        return str(results_path)
    
    def get_results(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get simulation results."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT results_path FROM runs WHERE id = ?",
                (run_id,)
            )
            row = cursor.fetchone()
        
        if row and row[0]:
            results_path = Path(row[0])
            if results_path.exists():
                with open(results_path) as f:
                    return json.load(f)
        
        return None
    
    def export_results_csv(self, run_id: str) -> Optional[str]:
        """Export results to CSV format."""
        results = self.get_results(run_id)
        if not results:
            return None
        
        # Convert series data to DataFrame
        df = pd.DataFrame(results['series'])
        
        # Pivot for better CSV format
        pivot_df = df.pivot(index='day', columns='metric', values='value')
        
        csv_path = f"data/results/{run_id}_timeseries.csv"
        pivot_df.to_csv(csv_path)
        
        return csv_path
    
    def get_all_simulations(self) -> List[Dict[str, Any]]:
        """Get all completed simulations with their scenarios and results."""
        simulations = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Get all completed runs
            cursor = conn.execute("""
                SELECT r.id, r.scenario_id, r.status, r.progress, r.message, r.started_at,
                       s.config as scenario_config, r.results_path
                FROM runs r
                JOIN scenarios s ON r.scenario_id = s.id
                WHERE r.status = 'done' AND r.results_path IS NOT NULL
                ORDER BY r.completed_at DESC
            """)
            runs = cursor.fetchall()
            
            for run in runs:
                run_id, scenario_id, status, progress, message, created_at, scenario_config, results_path = run
                
                try:
                    # Parse scenario
                    scenario_data = json.loads(scenario_config)
                    
                    # Load results if available
                    results_data = None
                    if results_path and Path(results_path).exists():
                        with open(results_path, 'r') as f:
                            results_data = json.load(f)
                    
                    if results_data:  # Only include runs with results
                        simulations.append({
                            'id': run_id,
                            'scenario_id': scenario_id,
                            'scenario': scenario_data,
                            'results': results_data,
                            'created_at': created_at
                        })
                
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    print(f"Error loading simulation data for run {run_id}: {e}")
                    continue
        
        return simulations