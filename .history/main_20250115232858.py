<<<<<<< Tabnine <<<<<<<
from fastapi import FastAPI
>>>>>>> Tabnine >>>>>>># {"conversationId":"8523b666-8e66-4aac-a2b6-23ce4133d4c3","source":"instruct"}
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