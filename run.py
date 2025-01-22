import uvicorn
import sys
from pathlib import Path

# Add the project root directory to Python path
root_path = Path(__file__).parent
sys.path.append(str(root_path))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
