from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - internship_service",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "internship_service", "status": "healthy"}
