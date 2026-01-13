from fastapi import FastAPI
from agent.api.api import api_router
from agent.core.config import settings

app = FastAPI(title="Lazy Budget API")

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Lazy Budget API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("agent.main:app", host="0.0.0.0", port=8000, reload=True)
