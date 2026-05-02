import uuid
from decimal import Decimal
from datetime import date, timedelta
from sqlmodel import Session, select
from src.db.session import engine, init_db
from src.models.masjid import Masjid
from src.models.user import User
from src.models.masjid_member import MasjidMember
from src.models.expense import Expense, RecurringExpenseTemplate
from src.core.security import get_password_hash

def seed_expenses():
    init_db()
    with Session(engine) as session:
        # Check if we have any masjid
        masjid = session.exec(select(Masjid)).first()
        if not masjid:
            print("Creating default masjid for seeding...")
            masjid = Masjid(
                name="Al-Noor Islamic Center",
                slug="al-noor",
                address="123 Faith Street",
                city="Dhaka",
                country="Bangladesh",
                contact_email="contact@alnoor.org"
            )
            session.add(masjid)
            session.commit()
            session.refresh(masjid)

        # Check if we have any user
        user = session.exec(select(User)).first()
        if not user:
            print("Creating default admin user for seeding...")
            user = User(
                email="admin@masjid.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            # Create membership
            membership = MasjidMember(
                masjid_id=masjid.id,
                user_id=user.id,
                role="admin",
                is_active=True
            )
            session.add(membership)
            session.commit()

        print(f"Seeding expenses for masjid: {masjid.name}")
        
        expenses = [
            {
                "title": "Electricity Bill - May 2026",
                "amount": Decimal("150.00"),
                "category": "Utility Bills",
                "expense_date": date.today(),
                "vendor": "Power Co",
                "payment_method": "Bank Transfer"
            },
            {
                "title": "Cleaning Supplies",
                "amount": Decimal("45.50"),
                "category": "Cleaning & Maintenance",
                "expense_date": date.today() - timedelta(days=2),
                "payment_method": "Cash"
            },
            {
                "title": "Imam Salary - May 2026",
                "amount": Decimal("2000.00"),
                "category": "Imam / Staff Salary",
                "expense_date": date.today() - timedelta(days=5),
                "vendor": "Imam Ahmed",
                "payment_method": "Bank Transfer"
            }
        ]

        for exp_data in expenses:
            expense = Expense(
                **exp_data,
                masjid_id=masjid.id,
                recorded_by=user.id
            )
            session.add(expense)
        
        # Add a recurring template
        template = RecurringExpenseTemplate(
            title="Monthly Water Bill",
            estimated_amount=Decimal("30.00"),
            category="Utility Bills",
            frequency="monthly",
            due_day_of_month=10,
            masjid_id=masjid.id,
            created_by=user.id
        )
        session.add(template)
        
        session.commit()
        print("Expense seeding completed successfully.")

if __name__ == "__main__":
    seed_expenses()
