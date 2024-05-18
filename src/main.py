from fastapi import HTTPException
from src.middleware.exception_handler import EnhancedTracebackMiddleware
from init import app

app = app
app.add_middleware(EnhancedTracebackMiddleware)


@app.get("/")
async def root():
    try:
        # 何らかの処理
        raise Exception("Internal Server Error")
    except Exception as e:
        raise HTTPException(status_code=500)