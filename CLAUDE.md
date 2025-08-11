# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ABM Communication Campaign Simulator - A full-stack application that simulates the effectiveness of communication campaigns using Agent-Based Modeling. Built with FastAPI backend, React frontend, and Mesa ABM framework.

## Quick Start

To start the application:

```bash
# Option 1: Use the launcher script
./run.sh

# Option 2: Start services manually
# Terminal 1 - Backend
python3 run_backend.py

# Terminal 2 - Frontend  
cd frontend && pnpm dev
```

Access the application at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture

### Backend (`backend/`)
- **FastAPI** server with async support
- **Mesa** ABM framework for simulation engine
- **NetworkX** for network generation and analysis
- **SQLite** for scenario/run metadata
- **JSON/CSV** export functionality

### Frontend (`frontend/`)
- **React + TypeScript + Vite** for fast development
- **Tailwind CSS** for styling
- **Recharts** for time series visualization
- **vis-network** for network visualization
- **Axios** for API communication

### Key Models
- **Customer Agent**: Individual entities with interest, receptivity, and influence attributes
- **Communication Model**: Controls media exposure, word-of-mouth propagation, and state transitions
- **Network Types**: Supports Erdős-Rényi, Watts-Strogatz, and Barabási-Albert networks

## Development Commands

### Backend
```bash
# Install dependencies (if not using global install)
uv sync

# Run with auto-reload
python3 run_backend.py

# Run tests (when implemented)
python3 -m pytest
```

### Frontend  
```bash
cd frontend

# Install dependencies
pnpm install

# Development server
pnpm dev

# Build for production
pnpm build

# Lint code
pnpm lint
```

## Configuration

- Backend server runs on port 8000
- Frontend development server runs on port 5173
- Database and results stored in `data/` directory
- Default simulation: 10k nodes, 60 days, 10 repetitions

## API Endpoints

Key endpoints:
- `POST /api/scenario` - Create simulation scenario
- `POST /api/run` - Start simulation run
- `GET /api/run/{id}/status` - Check run progress
- `GET /api/run/{id}/results` - Get simulation results
- `POST /api/network/preview` - Generate network preview
- `GET /api/run/{id}/export/csv` - Export results as CSV

## Troubleshooting

If services fail to start:
1. Check `backend.log` and `frontend.log` for errors
2. Ensure all dependencies are installed
3. Verify ports 5173 and 8000 are available
4. Kill existing processes: `pkill -f "run_backend.py" && pkill -f "pnpm dev"`

## Dependencies

Required Python packages: fastapi, uvicorn, mesa, networkx, numpy, pandas, pydantic, python-multipart, sqlalchemy, pyarrow

Required Node packages: react, typescript, vite, tailwindcss, recharts, vis-network, axios, lucide-react