from aiogram import Router

from .message import router as message_router
from .add import router as add_router
from .delete import router as delete_router
from .list import router as list_router
from .search import router as search_router

router = Router()

router.include_router(add_router)
router.include_router(delete_router)
router.include_router(search_router)
router.include_router(list_router)
router.include_router(message_router)
