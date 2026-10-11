from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class User(Base):
    """Registered user: login, password hash and a self-description for the coach.

    Attributes:
        id: primary key.
        login: unique user login.
        password_hash: argon2 hash of the password.
        description: user's self-description fed to the coach prompt (nullable).
        created_at: UTC row creation time (database-side default).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="user")
    generations: Mapped[list["Generation"]] = relationship(back_populates="user")


class Session(Base):
    """Login session: a unique token referenced by the httpOnly auth cookie.

    Attributes:
        id: primary key.
        token: unique urlsafe token stored in the auth cookie.
        user_id: foreign key to users.id.
        created_at: UTC row creation time (database-side default).
    """

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="sessions")


class Conversation(Base):
    """Chat with one person on a dating platform.

    Attributes:
        id: primary key.
        user_id: foreign key to users.id.
        platform: dating platform of the chat (nullable).
        match_name: display name of the chat partner (nullable).
        match_description: initial description of the chat partner (nullable).
        created_at: UTC row creation time (database-side default).
    """

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    platform: Mapped[str | None] = mapped_column(String(32))
    match_name: Mapped[str | None] = mapped_column(String(64))
    match_description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")
    generations: Mapped[list["Generation"]] = relationship(back_populates="conversation")


class Message(Base):
    """One message in a conversation.

    Attributes:
        id: primary key.
        conversation_id: foreign key to conversations.id.
        sender: message author — "me" (the user) or "match" (the partner).
        text: message body.
        sent_at: when the message was sent (nullable, edited in the UI).
        created_at: UTC row creation time (database-side default).
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    sender: Mapped[str] = mapped_column(String(8))
    text: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class Generation(Base):
    """Saved reply generation: the goal and serialized suggestions.

    Attributes:
        id: primary key.
        user_id: foreign key to users.id.
        conversation_id: foreign key to conversations.id.
        goal: user's goal for the reply (nullable).
        result_json: serialized Suggestions — three reply options.
        created_at: UTC row creation time (database-side default).
    """

    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    goal: Mapped[str | None] = mapped_column(String(64))
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="generations")
    conversation: Mapped["Conversation"] = relationship(back_populates="generations")
