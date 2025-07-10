from .support import router as support_router
# from .subscriptions import router as subscriptions_router
from .auth import router as auth_router

__all__ = ["support_router", "auth_router"]