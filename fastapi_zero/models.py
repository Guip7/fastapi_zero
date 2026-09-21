from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


def get_current_time():
    return datetime.now()


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
