"""Database models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedColumn, relationship


class Base(DeclarativeBase):
    pass


class UserBase(Base):
    __tablename__ = "users"

    id: Mapped[int] = MappedColumn(primary_key=True, autoincrement=True)
    cookies: Mapped[str] = MappedColumn(String(1024), nullable=False)
    created_at: Mapped[datetime] = MappedColumn(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = MappedColumn(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    urls: Mapped[list["UrlBase"]] = relationship(
        back_populates="owner"
    )
    summarizations: Mapped[list["SumBase"]] = relationship(back_populates="user")


class UrlBase(Base):
    __tablename__ = "urls"

    id: Mapped[int] = MappedColumn(primary_key=True, autoincrement=True)
    url: Mapped[str] = MappedColumn(String(2048), nullable=False)
    url_shortcode: Mapped[str] = MappedColumn(String(100), nullable=True)
    transcript_accessibility: Mapped[bool] = MappedColumn(Boolean, nullable=True)
    owner_id: Mapped[int] = MappedColumn(ForeignKey("users.id"), nullable=False)

    owner: Mapped["UserBase"] = relationship(
        back_populates="urls"
    )

    summarization: Mapped["SumBase"] = relationship(
        back_populates="url",
        uselist=False
    )


class SumBase(Base):
    __tablename__ = "summarization"

    id: Mapped[int] = MappedColumn(primary_key=True, autoincrement=True)
    user_owner_id: Mapped[int] = MappedColumn(ForeignKey("users.id"), nullable=False)
    url_owner_id: Mapped[int] = MappedColumn(ForeignKey("urls.id"), nullable=False)
    url_shortcode: Mapped[str] = MappedColumn(String(2048), nullable=False)
    path_to_sum_file: Mapped[str] = MappedColumn(String(2048), nullable=False)
    language_code: Mapped[str] = MappedColumn(String(100), nullable=True)
    created_at: Mapped[datetime] = MappedColumn(DateTime, default=datetime.utcnow)

    url: Mapped["UrlBase"] = relationship(
        back_populates="summarization"
    )

    user: Mapped["UserBase"] = relationship(
        back_populates="summarizations"
    )
