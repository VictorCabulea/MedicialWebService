from pydantic import BaseModel


class AccountDTO(BaseModel):
    last_name: str
    first_name: str
    user_name: str
    user_email: str
    password: str
