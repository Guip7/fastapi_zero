from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship
from sqlalchemy import ForeignKey, func
table_registry = registry()
from typing import List

def get_current_time():
    return datetime.now()

class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'

@table_registry.mapped_as_dataclass()
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    username: Mapped[str] = mapped_column(unique=True)

    email: Mapped[str] = mapped_column(unique=True)

    password: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        init=False,
        default=get_current_time,
    )

    todos: Mapped[List['Todo']] = relationship(
        init=False,
        cascade= 'all, delete-orphan',
        lazy='selectin'
    )

@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TodoState]

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))