import enum
from dataclasses import dataclass
from datetime import datetime as Datetime


class Role(str, enum.Enum):
    ADMIN = 'admin'
    GUEST = 'guest'
    USER = 'user'


@dataclass
class AuthInfo:
    user_id: int
    user_role: Role


@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    role: Role


@dataclass
class UserCredentials:
    user_id: int
    login: str
    password_hash: bytes


@dataclass
class UserToken:
    user_id: int
    token: str


@dataclass
class Post:
    id: int
    created_at: Datetime
    text: str
    image_url: str
    likes_quantity: int
    dislikes_quantity: int


class RateKind(str, enum.Enum):
    LIKE = 'like'
    DISLIKE = 'dislike'

@dataclass
class PostRate:
    id: int
    post_id: int
    user_id: int
    rate: RateKind

