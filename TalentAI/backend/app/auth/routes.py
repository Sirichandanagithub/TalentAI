from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.dependencies import get_current_user
from app.auth.models import User


from app.auth.schema import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    ChangePassword,
)

from app.auth.services import (
    create_user,
    authenticate_user,
)

from app.core.security import (
    create_access_token,
    verify_password,
    hash_password,
)

from app.database.session import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    return create_user(db, user_data)

#pydantic
# @router.post(
#     "/login",
#     response_model=Token,
# )
# def login(
#     user_data: UserLogin,
#     db: Session = Depends(get_db),
# ):
#     user = authenticate_user(
#         db,
#         user_data.email,
#         user_data.password,
#     )

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )

#     access_token = create_access_token(
#         data={"sub": user.email}
#     )

#     return Token(
#         access_token=access_token,
#         token_type="bearer",
#     )
#OAUTH2PasswordRequestForm
@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )
    #print("Authenticated user:", user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": user.email,
              "token_version": user.token_version},
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.post("/change-password")
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(
        password_data.current_password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    current_user.password_hash = hash_password(
        password_data.new_password
    )

    current_user.token_version += 1

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Password changed successfully. Please log in again."
    }