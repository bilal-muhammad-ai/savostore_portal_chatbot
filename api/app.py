from fastapi import FastAPI

from api.routes.health import router as health_router
from api.routes.bot import router as bot_router
app = FastAPI()
app.include_router(health_router)
app.include_router(bot_router)