#!/usr/bin/env python3
"""Simple script to run the backend server."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    import uvicorn
    from backend.app import app
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)