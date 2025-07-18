from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

from ..db import get_session
from ..models import User, Asset

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

@router.get("/paginated", response_model=list[User])
def read_users_paginated(
    skip: int = 0, 
    limit: int = 100, 
    session: Session = Depends(get_session)
):
    """
    Get users with pagination to reduce memory usage.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (capped at 500)
    
    Returns:
        List[User]: List of users
    """
    if limit > 500:  # Cap maximum limit
        limit = 500
        
    try:
        statement = select(User).offset(skip).limit(limit)
        return session.exec(statement).all()
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

@router.get("/{user_id}/assets", response_model=list[Asset])
def read_user_assets(user_id: int, session: Session = Depends(get_session)):
    """
    Get all assets assigned to a specific user.
    
    Args:
        user_id: The ID of the user whose assets to retrieve
        
    Returns:
        List[Asset]: List of assets assigned to the user
    """
    # First check if user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get assets assigned to this user
    try:
        statement = select(Asset).where(Asset.assigned_user_id == user_id)
        assets = session.exec(statement).all()
        return assets
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user assets: {str(e)}"
        ) 