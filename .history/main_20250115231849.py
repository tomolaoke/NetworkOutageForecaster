from fastapi import FastAPI
from datetime import datetime
import uvicorn

app = FastAPI(title="Network Outage Forecaster")

@app.get("/")
async def root():
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "message": "Network Outage Forecaster API"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)