from pydantic import BaseModel  # type: ignore

class LoginData(BaseModel):
    username: str
    password: str