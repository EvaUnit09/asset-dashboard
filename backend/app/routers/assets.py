from fastapi import APIRouter, Depends
from sqlmodel import select
from ..db import get_session
from ..models import Asset

router = APIRouter(prefix="/assets", tags=["assets"])

@router.get("", response_model=list[Asset])
def read_assets(session=Depends(get_session)):
    return session.exec(select(Asset)).all()


