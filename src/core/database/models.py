# from typing import List
#
# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column, relationship
#
# from core.database.base import Base
#
#
# class User(Base):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     telegram_id: Mapped[int] = mapped_column(unique=True)
#     movies: Mapped[List["Movie"]] = relationship("Movie", back_populates="user")
#
#
# class Movie(Base):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     title: Mapped[str]
#     imdb_rating: Mapped[float]
#     imdb_id: Mapped[str]
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     user: Mapped["User"] = relationship("User", back_populates="movies")



# if TYPE_CHECKING:
#     from src.auth.models import RefreshToken
#
#
# class User(Base):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     username: Mapped[str] = mapped_column(unique=True)
#     email: Mapped[str]
#     password: Mapped[str]
#     is_admin: Mapped[bool] = mapped_column(default=False)
#     refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
#         "RefreshToken",
#         cascade="all, delete",
#         back_populates="user",
#     )
#
#     def __repr__(self) -> str:
#         return f"User(id={self.id!r}, email={self.email!r})"
#
#     def __str__(self) -> str:
#         return f"User(id={self.id}, email={self.email})"
#
#
# if TYPE_CHECKING:
#     from src.users.models import User
#
#
# class RefreshToken(TimeStampModel):
#     """Refresh token model."""
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     token: Mapped[str] = mapped_column()
#     expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
#     revoked: Mapped[bool] = mapped_column(server_default=false())
#
#     user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
#
#     def __repr__(self) -> str:
#         return f"RefreshToken(id={self.id!r}, related_user={self.user_id!r})"
#
#     def __str__(self) -> str:
#         return f"RefreshToken(id={self.id}, related_user={self.user_id})"