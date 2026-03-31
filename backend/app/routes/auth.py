from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.database import get_db
from app.schemas.schemas import LoginRequest, UserResponse
from app.services.auth_service import authenticate_user
from app.utils.security import create_access_token, get_password_hash
from app.core.config import settings
from pydantic import BaseModel

class ChangePasswordRequest(BaseModel):
    newPassword: str

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class LoginResponse(UserResponse):
    """
    Combines the exact format expected by the frontend with a backend JWT token 
    so the frontend flow doesn't break, but allows for token scaling.
    """
    token: str

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user from the SQL Server database.
    Performs standard input cleaning (trimming) to avoid credential failure due to whitespace.
    """
    email = request.email.strip() if request.email else None
    employee_id = request.employee_id.strip() if request.employee_id else None
    
    logger.info(f"🔑 Login Attempt - Identifier: {email or employee_id} (Type: {'Email' if email else 'EmpID'})")
    
    user = authenticate_user(db, email=email, employee_id=employee_id, password=request.password)
    
    if not user:
        logger.warning(f"❌ Login Failed - Identifier: {email or employee_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Valid Database User
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    
    # We return the combination of UserResponse fields + token
    return {
        "id": user.id,
        "employeeId": user.employee_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "avatar": user.avatar,
        "projectId": user.project_id,
        "token": access_token
    }

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to be utilized by other protected endpoints.
    Allows passing the parsed generic token into standard User Database logic.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.error("Token payload missing 'sub' field.")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT Decode Error: {str(e)}")
        raise credentials_exception
    
    # We bypass DB check here for performance if we only care about role/id
    # But for a robust system, we would fetch and return the SQL user object.
    return {"id": user_id, "role": payload.get("role")}

@router.post("/change-password")
def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.models import User
    
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.password_hash = get_password_hash(request.newPassword)
    user.is_first_login = False
    db.commit()
    return {"message": "Password changed successfully"}

