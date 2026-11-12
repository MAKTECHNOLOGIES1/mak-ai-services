from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - mentorship_service",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "mentorship_service", "status": "healthy"}
