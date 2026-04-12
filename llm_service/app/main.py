from fastapi import FastAPI
from llm_service.app.routes import router
from llm_service.app.config import LLMConfig

app = FastAPI(
    title="LLM Service",
    description="Simple RAG LLM microservice",
    version="1.0.0"
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    config = LLMConfig.from_env()
    uvicorn.run(
        "llm_service.app.main:app",
        host=config.host,
        port=config.port,
        reload=False
    )