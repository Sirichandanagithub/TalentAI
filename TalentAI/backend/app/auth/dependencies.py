from jose import JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.models import User
from app.core.security import decode_access_token
from app.database.session import get_db


# Reads the JWT token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    print("=" * 50)
    print("Token received:", token)

    """
    Get the currently authenticated user.
    """

    print("=" * 50)
    print("Token received:", token)

    try:

        # Decode the JWT token
        payload = decode_access_token(token)
        print("Payload:", payload)

        # Get the email stored in the 'sub' claim
        email = payload.get("sub")
        print("Email from token:", email)

        # If no email is found, the token is invalid
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    except JWTError as e:
        print("JWT Error:", e)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Find the user in the database
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    print("User from DB:", user)
    print("=" * 50)

    # If user doesn't exist
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user