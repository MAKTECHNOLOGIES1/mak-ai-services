from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - faculty_ai_service",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "faculty_ai_service", "status": "healthy"}
