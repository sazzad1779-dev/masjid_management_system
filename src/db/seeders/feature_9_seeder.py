import uuid
from sqlmodel import Session, select
from datetime import datetime, timedelta
from src.models.notification import Notification
from src.models.user import User
from src.models.masjid import Masjid
from src.db.session import engine

def seed_notifications(db: Session):
    print("Seeding Notifications (Feature 9)...")
    
    # Get a masjid and its admin
    masjid = db.exec(select(Masjid)).first()
    if not masjid:
        print("No masjid found, skipping notification seeding.")
        return
        
    admin = db.exec(select(User).where(User.email == "admin@mms.app")).first()
    if not admin:
        print("No admin found, skipping notification seeding.")
        return
        
    # Get a donor user
    donor_user = db.exec(select(User).where(User.email == "user@mms.app")).first()

    notifications = [
        {
            "masjid_id": masjid.id,
            "user_id": admin.id,
            "type": "masjid_invitation",
            "title": "Masjid Invitation",
            "body": f"You have been invited to join {masjid.name} as admin.",
            "is_read": True,
            "created_at": datetime.now(UTC) - timedelta(days=10)
        },
        {
            "masjid_id": masjid.id,
            "user_id": admin.id,
            "type": "income_recorded",
            "title": "New Income Recorded",
            "body": "New income 'Friday Collection' of 5000.00 BDT has been recorded.",
            "is_read": False,
            "created_at": datetime.now(UTC) - timedelta(hours=2)
        },
        {
            "masjid_id": masjid.id,
            "user_id": admin.id,
            "type": "expense_recorded",
            "title": "New Expense Recorded",
            "body": "New expense 'Electricity Bill' of 3500.00 BDT has been recorded.",
            "is_read": True,
            "created_at": datetime.now(UTC) - timedelta(days=1)
        },
        {
            "masjid_id": masjid.id,
            "user_id": admin.id,
            "type": "low_balance",
            "title": "Low Balance Alert",
            "body": "Your Cash Box balance is below 1000.00 BDT.",
            "is_read": False,
            "created_at": datetime.now(UTC) - timedelta(minutes=30)
        },
        {
            "masjid_id": masjid.id,
            "user_id": admin.id,
            "type": "role_updated",
            "title": "Role Updated",
            "body": f"Your role at {masjid.name} has been updated to admin.",
            "is_read": True,
            "created_at": datetime.now(UTC) - timedelta(days=5)
        }
    ]
    
    if donor_user:
        notifications.append({
            "masjid_id": masjid.id,
            "user_id": donor_user.id,
            "type": "donation_verified",
            "title": "Donation Payment Verified",
            "body": "Your donation for 2026-05 has been verified. Thank you!",
            "is_read": False,
            "created_at": datetime.now(UTC) - timedelta(hours=5)
        })

    for n_data in notifications:
        # Check if exists
        existing = db.exec(select(Notification).where(
            Notification.user_id == n_data["user_id"],
            Notification.title == n_data["title"],
            Notification.body == n_data["body"]
        )).first()
        
        if not existing:
            n = Notification(**n_data)
            db.add(n)
            print(f"Added notification: {n.title} for {n_data['user_id']}")

    db.commit()
    print("Notification seeding completed.")

if __name__ == "__main__":
    from src.db.session import engine, init_db
    from datetime import UTC # ensure UTC is imported for datetime.now(UTC)
    init_db()
    with Session(engine) as session:
        seed_notifications(session)
