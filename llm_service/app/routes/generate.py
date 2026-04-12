from fastapi import APIRouter
from llm_service.app.models.schemas import GenerateRequest, GenerateResponse
from llm_service.app.services.queue import llm_queue

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    answer = await llm_queue.add_task(
        query=request.query,
        context=request.context
    )

    return GenerateResponse(answer=answer)