import enum
import pydantic as pd


class UserRole(str, enum.Enum):
    USER = 'user'
    ADMIN = 'admin'


class User(pd.BaseModel):
    name: str
    password: str
    role: UserRole