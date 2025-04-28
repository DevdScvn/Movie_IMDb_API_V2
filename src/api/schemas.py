from pydantic import BaseModel


class SUser(BaseModel):
    id: int
    username: str
    telegram_id: int


class SMovie(BaseModel):
    id: int
    title: str
    imdb_rating: float | None = None
    imdb_id: str
    user_id: int


class SMovieCreate(BaseModel):
    title: str
    imdb_id: str
    user_id: int
