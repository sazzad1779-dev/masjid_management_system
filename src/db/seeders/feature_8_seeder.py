import uuid
from sqlmodel import Session, select
from src.models.user import User
from src.models.masjid import Masjid
from src.models.account import Account
from src.models.income import Income
from src.models.expense import Expense
from src.models.donor import Donor
from src.models.donation import DonationRecord
from src.db.session import engine
from datetime import date, timedelta, datetime, UTC
from decimal import Decimal

def seed_reports(db: Session):
    print("Seeding Reporting & Analytics (Feature 8)...")
    
    # 1. Get existing masjid and admin
    masjid = db.exec(select(Masjid).where(Masjid.slug == "al-noor")).first()
    if not masjid:
        print("Masjid Al-Noor not found. Run auth_seeder first.")
        return
        
    admin = db.exec(select(User).where(User.email == "admin@mms.app")).first()
    if not admin:
        print("Admin user not found. Run auth_seeder first.")
        return

    # 2. Create an Account if not exists
    account = db.exec(select(Account).where(Account.masjid_id == masjid.id)).first()
    if not account:
        account = Account(
            masjid_id=masjid.id,
            account_name="Main Cash Box",
            account_type="Cash",
            opening_balance=1000.0,
            created_by=admin.id
        )
        db.add(account)
        db.commit()
        db.refresh(account)

    # 3. Seed Incomes for the last few months
    today = date.today()
    for i in range(1, 90): # last 90 days
        income_date = today - timedelta(days=i)
        income = Income(
            masjid_id=masjid.id,
            account_id=account.id,
            title=f"Sample Income {i}",
            amount=Decimal(str(100 + i * 2)),
            category="Friday Jumu'ah Collection" if i % 7 == 0 else "Sadaqah",
            income_date=income_date,
            recorded_by=admin.id
        )
        db.add(income)

    # 4. Seed Expenses for the last few months
    for i in range(1, 30):
        expense_date = today - timedelta(days=i*3)
        expense = Expense(
            masjid_id=masjid.id,
            account_id=account.id,
            title=f"Sample Expense {i}",
            amount=Decimal(str(50 + i * 5)),
            category="Utility Bills" if i % 3 == 0 else "Maintenance",
            expense_date=expense_date,
            recorded_by=admin.id
        )
        db.add(expense)

    # 5. Seed Donors and Donations
    donor = db.exec(select(Donor).where(Donor.masjid_id == masjid.id)).first()
    if not donor:
        donor = Donor(
            masjid_id=masjid.id,
            full_name="John Doe",
            phone="01711223344",
            email="john@example.com",
            monthly_pledge_amount=500.0,
            pledge_currency="USD",
            pledge_start_date=today - timedelta(days=60),
            payment_method="Cash",
            created_by=admin.id
        )
        db.add(donor)
        db.commit()
        db.refresh(donor)

    # Monthly donations
    for m_offset in range(0, 3):
        m_date = today - timedelta(days=m_offset*30)
        m_str = m_date.strftime("%Y-%m")
        existing_rec = db.exec(select(DonationRecord).where(
            DonationRecord.donor_id == donor.id,
            DonationRecord.month == m_str
        )).first()
        if not existing_rec:
            # Generate record
            rec = DonationRecord(
                masjid_id=masjid.id,
                donor_id=donor.id,
                month=m_str,
                pledged_amount=donor.monthly_pledge_amount,
                paid_amount=donor.monthly_pledge_amount if m_offset > 0 else 0,
                status="paid" if m_offset > 0 else "pending",
                payment_date=m_date if m_offset > 0 else None
            )
            db.add(rec)

    db.commit()
    print("Reporting seeding completed.")

if __name__ == "__main__":
    from src.db.session import init_db
    init_db()
    with Session(engine) as session:
        seed_reports(session)
