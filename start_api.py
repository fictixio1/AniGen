"""Start API server with PORT handling."""
import os
import subprocess
import sys

# Get PORT from environment, default to 8000
port = os.getenv('PORT', '8000')

# Start uvicorn
cmd = [
    'uvicorn',
    'api.main:app',
    '--host', '0.0.0.0',
    '--port', port
]

print(f"Starting API server on port {port}")
sys.exit(subprocess.call(cmd))
