from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str

class TransactionCreate(BaseModel):
    amount: float
    user_id: int