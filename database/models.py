from typing import List

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    tg_tag = mapped_column(String(30))
    role = mapped_column(String(30), default='user')
    domain_ids: Mapped[List['DomainId']] = relationship(back_populates='user')
    proxies: Mapped[List['Proxy']] = relationship(back_populates='user')
    texts: Mapped[List['Text']] = relationship(back_populates='user')


class DomainId(Base):
    __tablename__ = "domain_ids"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    user: Mapped["User"] = relationship(back_populates="domain_ids")


class Proxy(Base):
    __tablename__ = "proxies"

    id: Mapped[int] = mapped_column(primary_key=True)
    proxy: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    user: Mapped["User"] = relationship(back_populates="proxies")


class Text(Base):
    __tablename__ = "texts"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    user: Mapped["User"] = relationship(back_populates="texts")


class UserRequest(Base):
    __tablename__ = "user_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    tg_tag = mapped_column(String(30))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
