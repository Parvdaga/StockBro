from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.agents.master_agent import master_agent
from app.schemas import AgentResponse, StockData, NewsItem
import json

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "guest"

@router.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat with StockBro. 
    Accepts a natural language query and returns a structured response 
    containing the answer and any relevant stock/news data for the UI.
    """
    try:
        # Run the agent
        # stream=False for now to get the full response at once
        response_stream = master_agent.run(request.message, stream=False)
        
        # The agent returns a RunResponse object. 
        # We need to extract the content.
        # Phidata agents return .content as the string response.
        
        answer_text = response_stream.content
        
        # Parse for structured data (Strategy: Agent dumps JSON in <json> tags or we infer?)
        # For now, we'll keep it simple: The text is the answer.
        # Future improvement: Instruct agent to return JSON string in a specific block.
        
        # Attempt to extract simple structure if the agent used tools and found data
        # This is a simplification. Real implementation might parse tool outputs.
        
        stocks = []
        news = []
        
        # TODO: Enhanced parsing of agent "messages" or "tool_calls" to populate stocks/news
        
        return AgentResponse(
            answer=answer_text,
            stocks=stocks,
            news=news
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    return {"status": "ok", "agent": "StockBro Ready"}
