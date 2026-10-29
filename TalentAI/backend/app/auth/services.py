from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.schema import UserCreate
from app.core.security import (
    hash_password,
    verify_password,
)


def create_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    """
    Create a new user with a securely hashed password.
    """

    hashed_password = hash_password(
        user_data.password
    )

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    """
    Authenticate a user using email and password.

    Returns the user when credentials are valid.
    Returns None when authentication fails.
    """

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user