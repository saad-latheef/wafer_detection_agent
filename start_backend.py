"""
Startup script for backend server with proper PYTHONPATH
"""
import os
import sys

# Add project root to Python path for google.adk module
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = project_root

print(f"✅ PYTHONPATH set to: {project_root}")
print(f"✅ sys.path includes: {project_root}")

# Now start uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.server:app", 
        host="0.0.0.0",
        port=8000,
        reload=True
    )
