from dataclasses import asdict
import pytest
from sqlalchemy import select

from fastapi_zero.models import User

from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):

    async with mock_db_time(model=User) as time:
        new_user = User(
            username="test",
            email="test@gmail.com",
            password="secret",
        )
        
        session.add(new_user)
        await session.commit()

        user = await session.scalar(select(User).where(User.username == "test"))

        assert asdict(user) == {
            "id": 1,
            "username": "test",
            "email": "test@gmail.com",
            "password": "secret",
            "created_at": time,
        }
