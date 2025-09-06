"""Simple script to run the Guardian Layer API"""

import uvicorn
import sys
import os

# Add the parent directory to the path so we can import guardian_app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_api():
    """Run the Guardian Layer API server"""
    uvicorn.run(
        "guardian_app.api.guardian_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    print("Starting Guardian Layer API...")
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    run_api()
