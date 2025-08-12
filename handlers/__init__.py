# from .support import router as support_router
# from .subscriptions import router as subscriptions_router
from .auth import router as auth_router
from .subscriptions import router as subscriptions_router
from .cabinet import router as cabinet_router

__all__ = ["auth_router", "subscriptions_router", "cabinet_router"]