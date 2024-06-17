from src.endpoint import auth_endpoint
from src.middleware.exception_handler import EnhancedTracebackMiddleware
from src.init import app
from src.endpoint import user_endpoint
from src.endpoint import chat_endpoint
from src.endpoint import guest_user_endpoint

app = app
app.add_middleware(EnhancedTracebackMiddleware)

#router
app.include_router(user_endpoint.router)
app.include_router(auth_endpoint.router)
app.include_router(chat_endpoint.router)
app.include_router(guest_user_endpoint.router)