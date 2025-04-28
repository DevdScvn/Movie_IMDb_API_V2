from sqlalchemy import select

from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import User, Movie


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, session: AsyncSession):
        stmt = select(cls.model).order_by(cls.model.id)
        result = await session.scalars(stmt)
        return result.all()

        # stmt = select(User).order_by(User.id)
        # result = await session.scalars(stmt)
        # return result.all()

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        query = select(cls.model.__table__.columns).filter_by(**filter_by)
        result = await session.execute(query)
        return result.mappings().one_or_none()

    @classmethod
    async def add(cls, data, session: AsyncSession) -> model:
        query = cls.model(**data.model_dump())
        session.add(query)
        await session.commit()
        await session.refresh(query)
        return query

    @classmethod
    async def register_add(cls, session: AsyncSession, **data) -> model:
        query = insert(cls.model).values(**data).returning(cls.model.id)
        await session.execute(query)
        await session.commit()

    @classmethod
    async def del_one(cls, session: AsyncSession, **filter_by):
        query = delete(cls.model).filter_by(**filter_by)
        await session.execute(query)
        await session.commit()


class UserDAO(BaseDAO):
    model = User


class MovieDAO(BaseDAO):
    model = Movie




