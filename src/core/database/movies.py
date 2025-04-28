from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


if TYPE_CHECKING:
    from core.database.models import User


class Movie(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    imdb_rating: Mapped[Optional[float]] = mapped_column(nullable=True)
    imdb_id: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="movies")

