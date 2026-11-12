from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - career_service",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "career_service", "status": "healthy"}
