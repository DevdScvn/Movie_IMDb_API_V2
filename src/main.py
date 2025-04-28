from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI
from starlette.requests import Request

from bot.create_bot import dp, bot, stop_bot, start_bot
from bot.handlers import user_router
from core.config import settings
from core.database.db_helper import db_helper
from api.router import router as movie_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    #startup
    dp.include_router(user_router)
    await start_bot()
    webhook_url = settings.get_webhook_url()
    await bot.set_webhook(url=webhook_url,
                          allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)
    yield
    #shutdown
    print("dispose_engine")
    await db_helper.dispose()
    await bot.delete_webhook()
    await stop_bot()

main_app = FastAPI(
    lifespan=lifespan,
)


@main_app.post("/webhook")
async def webhook(request: Request) -> None:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)

main_app.include_router(movie_router)

if __name__ == "__main__":
    uvicorn.run("main:main_app",
                host=settings.run.host,
                port=settings.run.port,
                reload=True)


