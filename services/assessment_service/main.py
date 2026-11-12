from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - assessment_service",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "assessment_service", "status": "healthy"}

# Cloudflare Workers Python ASGI Handler
async def on_fetch(request, env):
    try:
        import asgi
        return await asgi.fetch(app, request, env)
    except ImportError:
        return app
