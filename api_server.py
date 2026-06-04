import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
from core.orchestrator import Orchestrator
import logging

# ตั้งค่า Logging แบบ Production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("logs/api.log"), logging.StreamHandler()]
)
logger = logging.getLogger("JinxAPI")

app = FastAPI(title="Jinx Agent API", version="2.0.0")
jinx = Orchestrator()

# Data Model สำหรับรับ Request
class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: dict = {}

# Data Model สำหรับส่ง Response
class ChatResponse(BaseModel):
    status: str
    timestamp: str
    response: str
    metadata: dict

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "Jinx Cognitive Engine"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received message from {request.user_id}: {request.message}")
        
        # ส่ง Input เข้า Orchestrator หลักของ Jinx
        start_time = datetime.now()
        result = jinx.run(request.message)
        latency = (datetime.now() - start_time).total_seconds() * 1000

        return ChatResponse(
            status="success",
            timestamp=datetime.now().isoformat(),
            response=result,
            metadata={
                "latency_ms": round(latency, 2),
                "user_id": request.user_id
            }
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Brain Error")

@app.post("/memory/reset")
def reset_memory(user_id: str):
    jinx.reset_memory()
    return {"message": f"Memory for session reset successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
