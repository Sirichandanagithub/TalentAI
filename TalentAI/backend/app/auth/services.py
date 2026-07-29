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

    hashed_password = hash_password(user_data.password)

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
    print("Email received:", email)

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )
    print("User found:", user)
    
    if user is None:
        return None

    print("Password entered:", password)
    print("Password hash:", user.password_hash)

    is_valid = verify_password(password, user.password_hash)
    print("Password valid:", is_valid)

    if not is_valid:
        return None

    return user