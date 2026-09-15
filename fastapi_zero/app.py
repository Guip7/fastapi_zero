from http import HTTPStatus, 

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fastapi_zero.schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()

database = []


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Olá mundo"}


@app.get("/html", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def html_helloworld():
    return """
     <html>
      <head>
        <title>Nosso olá mundo!</title>
      </head>
      <body>
        <h1> Olá Mundo </h1>
      </body>
    </html>
    """


@app.post("/users/", status_code=HTTPStatus.OK, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = database(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)
    return user


@app.get("/users", status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
  return {"users": database}

@app.put("/users/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(user_id: int,user: UserSchema)

    user_with_id = UserDB(**user.model_dump(), id=(database))

    if user_id < 1 or user_id > len(database):
      raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail='Deu ruim! Não achei'
      )
    
    database[user_id - 1] = user_with_id

    return user_with_id

@app.delete("/users/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Deu ruim! Não achei"
        )

    database.pop(user_id - 1)

    return