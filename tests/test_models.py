from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.models import Base, Conversation, Generation, Message, Session, User


@pytest.fixture
async def db_session() -> AsyncSession:
    """Session over a fresh in-memory database with all tables created."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def create_user(db_session: AsyncSession, login: str = "misha") -> User:
    """Persist and return a user with the given login."""
    user = User(login=login, password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    return user


async def test_user_created(db_session: AsyncSession) -> None:
    """A user is persisted with an id, nullables and a creation timestamp."""
    user = await create_user(db_session)
    await db_session.refresh(user)

    assert user.id is not None
    assert user.created_at is not None
    assert user.description is None


async def test_session_belongs_to_user(db_session: AsyncSession) -> None:
    """A session links to its user from both sides."""
    user = User(login="misha", password_hash="hash")
    auth_session = Session(token="token-123", user=user)
    db_session.add(auth_session)
    await db_session.commit()

    assert auth_session.user_id == user.id
    assert user.sessions == [auth_session]


async def test_conversation_holds_messages(db_session: AsyncSession) -> None:
    """Messages keep sender, text and time inside a conversation."""
    user = await create_user(db_session)
    conversation = Conversation(
        user=user,
        platform="tinder",
        match_name="Alice",
    )
    first = Message(
        conversation=conversation,
        sender="match",
        text="Привет!",
        sent_at=datetime(2026, 10, 1, 12, 0, tzinfo=UTC),
    )
    second = Message(
        conversation=conversation,
        sender="me",
        text="Привет)",
        sent_at=None,
    )
    db_session.add_all([first, second])
    await db_session.commit()

    assert conversation.id is not None
    assert conversation.match_description is None
    assert {message.text for message in conversation.messages} == {"Привет!", "Привет)"}
    assert first.sent_at is not None
    assert second.sent_at is None


async def test_generation_links_user_and_conversation(
    db_session: AsyncSession,
) -> None:
    """A generation references both its user and the conversation."""
    user = User(login="misha", password_hash="hash")
    conversation = Conversation(user=user)
    generation = Generation(
        user=user,
        conversation=conversation,
        goal="get a date",
        result_json='{"suggestions": []}',
    )
    db_session.add(generation)
    await db_session.commit()

    assert generation.conversation_id == conversation.id
    assert conversation.generations == [generation]
    assert user.generations == [generation]


async def test_duplicate_login_rejected(db_session: AsyncSession) -> None:
    """A duplicate login violates the unique constraint."""
    await create_user(db_session)
    db_session.add(User(login="misha", password_hash="hash2"))

    with pytest.raises(IntegrityError):
        await db_session.commit()
