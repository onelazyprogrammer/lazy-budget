from agent.schemas.chat import ChatRequest
from fastapi import APIRouter, HTTPException
from agent.core.agent import agent

router = APIRouter()


@router.post("/")
async def chat(message: ChatRequest):
    try:
        result = await agent.get_response(message.messages)

        return result

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
