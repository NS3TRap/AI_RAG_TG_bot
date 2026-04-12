from fastapi import APIRouter
from llm_service.app.models.schemas import GenerateRequest, GenerateResponse
from llm_service.app.services.llm import LLMService
from llm_service.app.services.queue import LLMQueue

router = APIRouter()
llm_service = LLMService()
llm_queue = LLMQueue(llm_service)


@router.on_event("startup")
async def startup():
    await llm_queue.start()

@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    answer = await llm_queue.add_task(
        query=request.query,
        context=request.context
    )

    return GenerateResponse(answer=answer)