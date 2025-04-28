from typing import Annotated, List, Dict

from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from api.router import get_user_movies
from core.database import Movie
from core.database.db_helper import db_helper
from core.database.users import User
from dao.basedao import MovieDAO

user_router = Router()


async def set_user(username: str, telegram_id: int):
    async with db_helper.session_factory() as session:
        user = await session.scalar(select(User).filter_by(telegram_id=telegram_id))
        # user = await UserDAO.find_one_or_none(session, filter_by=telegram_id)
        if not user:
            new_user = User(username=username, telegram_id=telegram_id)
            session.add(new_user)
            await session.commit()
            # new_user = UserDAO.add(username, telegram_id, session)
            # await session.execute(new_user)
            # await session.commit()


@user_router.message(CommandStart())
async def cmd_start(message: Message):
    user = await set_user(

        username=message.from_user.username,
        telegram_id=message.from_user.id, )
    # if not user:
    #     greeting = f"Привет, новый пользователь! Выбери необходимое действие"
    greeting = f"Привет, {message.from_user.username}! Выбери необходимое действие"
    # greeting = f"Привет, новый пользователь! Выбери необходимое действие"

    await message.answer(greeting)
    # return user


# async def search_movies(query: str):
#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"http://www.omdbapi.com/?apikey=95bb1ea4&s={query}"
#         )
#         return response.json().get("Search", [])


# async def search_movies(query: str) -> List[Dict[str, str]]:
#     """
#     Ищет фильмы через OMDb API и возвращает список с ключевыми данными:
#     - title (название)
#     - imdbID (уникальный ID в IMDb)
#     - Year (год выпуска)
#     """
#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"http://www.omdbapi.com/?apikey=ваш_ключ&s={query}"
#         )
#         data = response.json()
#
#         # Обрабатываем ответ API
#         if data.get("Response") == "True":
#             return [
#                 {
#                     "title": movie.get("Title"),
#                     "imdbID": movie.get("imdbID"),
#                     "Year": movie.get("Year")
#                 }
#                 for movie in data["Search"]
#             ]
#         return []


# @user_router.message(Command("add"))
# async def add_movie(message: Message):
#     async with db_helper.session_factory() as session:
#         query = message.text.replace("/add", "").strip()
#         if not query:
#             await message.answer("Укажите название фильма: /add Название")
#         movies = await search_movies(query)
#         res = await MovieDAO.find_one_or_none(session, title=movies)
#         # result = session.add(res)
#         # return result
#         return res



# @user_router.message(Command("add"))
# async def add_movie(message: types.Message):
#     query = message.text.replace("/add", "").strip()
#     if not query:
#         await message.answer("Укажите название фильма: /add Название")
#         return
#
#     movies = await search_movies(query)
#     if not movies:
#         await message.answer("Фильмы не найдены. Попробуйте другое название.")
#         return
#
#     # Формируем список для вывода пользователю
#     movies_list = "\n".join(
#         [f"{i+1}. {m['title']} ({m['Year']})" for i, m in enumerate(movies)]
#     )
#     await message.answer(
#         f"Найдены фильмы:\n{movies_list}\n\n"
#         "Ответьте номером фильма, чтобы добавить его."
#     )





# @user_router.message(Command("add"))
# async def add_movie(message: types.Message, db: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
#     query = message.text.replace("/add", "").strip()
#     if not query:
#         await message.answer("Укажите название фильма: /add Название")
#     movies = await search_movies(query)
#     await db.scalar(select(Movie))
#     return db.add(movies)



@user_router.message(Command("list"))
async def list_movies(message: Message):
    async with db_helper.session_factory() as session:
        movies = await get_user_movies(session, message.from_user.id)
        if not movies:
            await message.answer("Ваш список фильмов пуст.")
            return
    response = "📽 Ваши фильмы:\n\n"
    for movie in movies:
        response += f"▪ {movie.title} (⭐ {movie.imdb_rating})\n"
    await message.answer(response)
    return response


async def search_movies(query: str, user_id: int) -> List[Dict[str, str]]:
    """
    Универсальная функция для поиска фильмов.
    Возвращает:
    - title (название),
    - imdb_id (ID в IMDb),
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"http://www.omdbapi.com/?apikey=95bb1ea4&s={query}"
            )
            response.raise_for_status()  # Проверка HTTP-ошибок
            data = response.json()

            if data.get("Response") == "True":
                return [
                    {
                        "title": movie.get("Title"),
                        "imdb_id": movie.get("imdbID"),
                        "user_id": user_id
                    }
                    for movie in data["Search"]
                ]
            return []

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при запросе к IMDb API: {str(e)}"
            )


async def get_user_by_telegram_id(telegram_id: int):
    async with db_helper.session_factory() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
    return result.scalar_one_or_none()


@user_router.message(Command("add"))
async def add_movie(message: types.Message):
    async with db_helper.session_factory() as session:
        user = await get_user_by_telegram_id(message.from_user.id)

        query = message.text.replace("/add", "").strip()
        if not query:
            await message.answer("Укажите название фильма: /add Название")
        movies = await search_movies(query, user.id)
        await MovieDAO.register_add(session, **movies[0])
    return movies[0]


    # movies = await search_movies(query)
    # await MovieDAO.register_add(db, **movies[0])
    # if not movies:
    #     raise HTTPException(status_code=404, detail="Фильмы не найдены")
    # return movies[0]