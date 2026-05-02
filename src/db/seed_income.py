from sqlmodel import Session, select
from src.db.session import engine
from src.models.income import Income
from src.models.masjid import Masjid
from src.models.user import User
from decimal import Decimal
from datetime import date, timedelta, UTC, datetime
import uuid

def seed_income():
    with Session(engine) as session:
        # Get first masjid
        masjid = session.exec(select(Masjid)).first()
        if not masjid:
            print("No masjid found. please seed masjid data first.")
            return
        
        # Get admin user
        admin = session.exec(select(User).where(User.role == "super_admin")).first()
        if not admin:
            # Fallback to any user
            admin = session.exec(select(User)).first()
        
        if not admin:
            print("No user found. Please seed user data first.")
            return

        # Seed Income Data
        income_count = session.exec(select(Income).where(Income.masjid_id == masjid.id)).all()
        if len(income_count) == 0:
            print(f"Seeding income data for Masjid: {masjid.name}...")
            
            categories = [
                "Friday Jumu'ah Collection",
                "Daily Prayer Collection",
                "Zakat",
                "Sadaqah",
                "Rental Income"
            ]
            
            # Create some records for the last 4 weeks
            today = date.today()
            for i in range(20):
                income_date = today - timedelta(days=i)
                category = categories[i % len(categories)]
                title = f"{category} - {income_date}"
                amount = Decimal("100.00") + Decimal(i * 50)
                
                income = Income(
                    masjid_id=masjid.id,
                    title=title,
                    amount=amount,
                    category=category,
                    income_date=income_date,
                    payment_method="Cash",
                    recorded_by=admin.id,
                    currency=masjid.currency
                )
                session.add(income)
            
            session.commit()
            print("Successfully seeded income data.")
        else:
            print("Income data already exists.")

if __name__ == "__main__":
    seed_income()
