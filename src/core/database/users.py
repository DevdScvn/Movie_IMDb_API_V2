from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from core.database.models import Movie


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    movies: Mapped[List["Movie"]] = relationship("Movie", back_populates="user")
