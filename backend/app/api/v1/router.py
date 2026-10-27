from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from . import schemas
from ...database import get_db
from ... import models

router = APIRouter()

# ---------- Account Endpoints ----------
@router.get("/accounts", response_model=List[schemas.AccountRead])
def list_accounts(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db)):
    accounts = db.query(models.Account).offset(skip).limit(limit).all()
    return accounts

@router.post("/accounts", response_model=schemas.AccountRead)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = models.Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

# ---------- Quote Endpoints ----------
@router.get("/quotes", response_model=List[schemas.QuoteRead])
def list_quotes(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db)):
    quotes = db.query(models.Quote).offset(skip).limit(limit).all()
    return quotes

@router.post("/quotes", response_model=schemas.QuoteRead)
def create_quote(quote: schemas.QuoteCreate, db: Session = Depends(get_db)):
    # Ensure account exists
    account = db.query(models.Account).filter(models.Account.id == quote.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db_quote = models.Quote(**quote.dict())
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return db_quote
