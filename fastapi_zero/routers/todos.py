from fastapi import APIRouter, Depends, Query, HTTPException
from ..schemas import (TodoSchema, 
                       TodoPublic, 
                       FilterTodo, 
                       TodoList, 
                       Message,
                       TodoUpdate
)
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User, Todo
from ..database import get_session
from ..security import get_current_user
from sqlalchemy import select
from http import HTTPStatus

router = APIRouter(prefix='/todo', tags=['todos'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post('/', response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema,
    user: CurrentUser ,
    session: Session
):
    db_todo = Todo(
        title = todo.title,
        description= todo.description,
        state=todo.state,
        user_id=user.id
    )

    session.add(db_todo)

    await session.commit()
    await session.refresh(db_todo)

@router.get('/', response_model=TodoList)
async def list_todos(
    user: CurrentUser,
    session: Session,
    todo_filter: Annotated[FilterTodo, Query()]
):
    query = select(Todo).where (Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))
    if todo_filter.description:
        query = query.filter(Todo.description.contains(todo_filter.description))
    if todo_filter.state:
        query = query.filter(Todo.state == todo_filter.state)

    todos = await session.scalars(
        query.limit(todo_filter.limit).offset(todo_filter.offset)
    )

    return {'todos': todos.all()}

@router.delete('/{todo_id}', response_model=Message)
async def delete_todo(todo_id: int, session: Session, user: CurrentUser):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task has been deleted successfully.'}

@router.patch('/{todo_id}', response_model=TodoPublic)
async def patch_todo(
    todo_id: int, session: Session, user: CurrentUser, todo: TodoUpdate
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

        session.add(db_todo)
        await session.commit()
        await session.refresh(db_todo)

        return db_todo