import uuid
from typing import List, Optional
from sqlmodel import Session, select, func
from src.models.account import Account, AccountTransfer
from src.models.income import Income
from src.models.expense import Expense
from src.schemas.account import AccountCreate, AccountUpdate, AccountTransferCreate

def create_account(db: Session, *, obj_in: AccountCreate, masjid_id: uuid.UUID, user_id: uuid.UUID) -> Account:
    db_obj = Account(
        **obj_in.model_dump(),
        masjid_id=masjid_id,
        created_by=user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_account(db: Session, account_id: uuid.UUID) -> Optional[Account]:
    return db.get(Account, account_id)

def get_accounts(db: Session, *, masjid_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Account]:
    statement = select(Account).where(Account.masjid_id == masjid_id).offset(skip).limit(limit)
    return db.exec(statement).all()

def update_account(db: Session, *, db_obj: Account, obj_in: AccountUpdate) -> Account:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_account_balance(db: Session, *, account_id: uuid.UUID, masjid_id: uuid.UUID) -> float:
    account = db.get(Account, account_id)
    if not account or account.masjid_id != masjid_id:
        return 0.0
    
    opening_balance = account.opening_balance
    
    # Total Income for this account
    income_statement = select(func.sum(Income.amount)).where(
        Income.account_id == account_id,
        Income.is_deleted == False
    )
    total_income = db.exec(income_statement).one() or 0.0
    
    # Total Expense for this account
    expense_statement = select(func.sum(Expense.amount)).where(
        Expense.account_id == account_id,
        Expense.is_deleted == False
    )
    total_expense = db.exec(expense_statement).one() or 0.0
    
    # Transfers FROM this account (Reduces balance)
    transfer_out_statement = select(func.sum(AccountTransfer.amount)).where(
        AccountTransfer.from_account_id == account_id
    )
    total_transfer_out = db.exec(transfer_out_statement).one() or 0.0
    
    # Transfers TO this account (Increases balance)
    transfer_in_statement = select(func.sum(AccountTransfer.amount)).where(
        AccountTransfer.to_account_id == account_id
    )
    total_transfer_in = db.exec(transfer_in_statement).one() or 0.0
    
    current_balance = opening_balance + float(total_income) - float(total_expense) - float(total_transfer_out) + float(total_transfer_in)
    return current_balance

def create_transfer(db: Session, *, obj_in: AccountTransferCreate, masjid_id: uuid.UUID, user_id: uuid.UUID) -> AccountTransfer:
    db_obj = AccountTransfer(
        **obj_in.model_dump(),
        masjid_id=masjid_id,
        recorded_by=user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_transfers(db: Session, *, masjid_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[AccountTransfer]:
    statement = select(AccountTransfer).where(AccountTransfer.masjid_id == masjid_id).offset(skip).limit(limit)
    return db.exec(statement).all()
