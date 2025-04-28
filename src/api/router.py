from typing import Annotated, Sequence, List, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import SUser, SMovie, SMovieCreate
from core.database import db_helper, Movie, User
from dao.basedao import UserDAO, MovieDAO

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


async def get_user_movies(db: AsyncSession, telegram_id: int):
    result = await db.execute(
        select(Movie).join(User).where(User.telegram_id == telegram_id)
    )
    return result.scalars().all()


@router.get("/movies")
async def list_movies(telegram_id: int, db: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    return await get_user_movies(db, telegram_id)


@router.get("/get_all_users", response_model=Sequence[SUser])
async def get_users(db: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    # stmt = select(User).order_by(User.id)
    # result = await session.scalars(stmt)
    # return result.all()
    query = await UserDAO.find_all(db)
    return query


@router.post("/add_movies", response_model=SMovie)
async def add_movie(data: SMovie,
                    db: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    query = await MovieDAO.add(data, db)
    return query


@router.get("/get_all_movies", response_model=Sequence[SMovie])
async def get_all__movies(db: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    query = await MovieDAO.find_all(db)
    return query
    # stmt = select(Movie).order_by(Movie.id)
    # result = await db.scalars(stmt)
    # return result.all()


async def search_movies(query: str) -> List[Dict[str, str]]:
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
                        "user_id": 1
                    }
                    for movie in data["Search"]
                ]
            return []

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при запросе к IMDb API: {str(e)}"
            )


@router.get("/search", response_model=SMovieCreate)
async def search_movies_endpoint(query: str,
                                 db: Annotated[AsyncSession, Depends(db_helper.session_getter)]):
    """
    Поиск фильмов через IMDb API.
    Возвращает список с полями: title, imdbID, Year.

    Пример запроса:
    /api/movies/search?query=Matrix
    """
    movies = await search_movies(query)
    await MovieDAO.register_add(db, **movies[0])
    if not movies:
        raise HTTPException(status_code=404, detail="Фильмы не найдены")
    return movies[0]
