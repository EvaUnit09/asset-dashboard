from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

from ..db import get_session
from ..models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[User])
def read_users(session: Session = Depends(get_session)):
    """
    Get all users from the database.
    
    Returns:
        List[User]: List of all users
    """
    try:
        return session.exec(select(User)).all()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch users: {str(e)}"
        )

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, session: Session = Depends(get_session)):
    """
    Get a specific user by ID.
    
    Args:
        user_id: The ID of the user to retrieve
        
    Returns:
        User: The user object
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user 