import uuid
from datetime import datetime, UTC, date
from sqlmodel import Session, select
from src.db.session import engine, init_db
from src.models.masjid import Masjid
from src.models.user import User
from src.models.account import Account, AccountTransfer
from src.models.income import Income
from src.models.expense import Expense
from src.core.security import get_password_hash

def seed_feature_6():
    init_db()
    with Session(engine) as session:
        # Get masjid
        masjid = session.exec(select(Masjid)).first()
        if not masjid:
            print("No masjid found. Please seed masjid first.")
            return

        # Get user
        user = session.exec(select(User)).first()
        if not user:
            print("No user found. Please seed user first.")
            return

        print(f"Seeding accounts for masjid: {masjid.name}")
        
        # Create Accounts
        cash_acc = Account(
            masjid_id=masjid.id,
            account_name="General Cash Box",
            account_type="Cash",
            opening_balance=1000.0,
            created_by=user.id
        )
        bank_acc = Account(
            masjid_id=masjid.id,
            account_name="Main Bank Account",
            account_type="Bank",
            bank_name="Islamic Bank",
            account_number="123456789",
            opening_balance=5000.0,
            created_by=user.id
        )
        mobile_acc = Account(
            masjid_id=masjid.id,
            account_name="bKash Merchant",
            account_type="Mobile Banking",
            account_number="01711223344",
            opening_balance=500.0,
            created_by=user.id
        )
        
        session.add_all([cash_acc, bank_acc, mobile_acc])
        session.commit()
        session.refresh(cash_acc)
        session.refresh(bank_acc)
        session.refresh(mobile_acc)
        
        print("Accounts seeded.")
        
        # Create some Income linked to accounts
        income1 = Income(
            masjid_id=masjid.id,
            account_id=cash_acc.id,
            title="Friday Collection",
            amount=500.0,
            category="Friday Jumu'ah Collection",
            income_date=date.today(),
            payment_method="Cash",
            recorded_by=user.id
        )
        income2 = Income(
            masjid_id=masjid.id,
            account_id=bank_acc.id,
            title="Monthly Donation - Br. Karim",
            amount=200.0,
            category="Monthly Donation",
            income_date=date.today(),
            payment_method="Bank Transfer",
            recorded_by=user.id
        )
        session.add_all([income1, income2])
        
        # Create some Expenses linked to accounts
        expense1 = Expense(
            masjid_id=masjid.id,
            account_id=cash_acc.id,
            title="Cleaning Soap",
            amount=20.0,
            category="Cleaning & Maintenance",
            expense_date=date.today(),
            payment_method="Cash",
            recorded_by=user.id
        )
        session.add_all([expense1])
        
        # Create a Transfer (Cash to Bank)
        transfer = AccountTransfer(
            masjid_id=masjid.id,
            from_account_id=cash_acc.id,
            to_account_id=bank_acc.id,
            amount=400.0,
            currency="USD",
            notes="Depositing cash to bank",
            recorded_by=user.id
        )
        session.add(transfer)
        
        session.commit()
        print("Transfers and linked transactions seeded.")
        
        # Verify balances
        from src.crud.crud_account import get_account_balance
        
        cash_balance = get_account_balance(session, account_id=cash_acc.id, masjid_id=masjid.id)
        bank_balance = get_account_balance(session, account_id=bank_acc.id, masjid_id=masjid.id)
        
        print(f"Cash Balance: {cash_balance} (Expected: 1000 + 500 - 20 - 400 = 1080)")
        print(f"Bank Balance: {bank_balance} (Expected: 5000 + 200 + 400 = 5600)")

if __name__ == "__main__":
    seed_feature_6()
