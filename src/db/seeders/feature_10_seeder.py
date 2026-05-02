import uuid
from sqlmodel import Session, select
from datetime import datetime, timedelta, UTC
from src.models.audit_log import AuditLog
from src.models.user import User
from src.models.masjid import Masjid
from src.db.session import engine

def seed_audit_logs(db: Session):
    print("Seeding Audit Logs (Feature 10)...")
    
    # Get a masjid and its admin
    masjid = db.exec(select(Masjid)).first()
    if not masjid:
        print("No masjid found, skipping audit log seeding.")
        return
        
    admin = db.exec(select(User).where(User.email == "admin@mms.app")).first()
    if not admin:
        print("No admin found, skipping audit log seeding.")
        return
        
    audit_logs = [
        {
            "masjid_id": masjid.id,
            "user_id": admin.id,
            "user_name": admin.email,
            "action": "login",
            "entity_type": "user",
            "entity_id": admin.id,
            "details": "User logged in successfully",
            "ip_address": "127.0.0.1",
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "created_at": datetime.now(UTC) - timedelta(days=5)
        },
        {
            "masjid_id": masjid.id,
            "user_id": admin.id,
            "user_name": admin.email,
            "action": "create",
            "entity_type": "income",
            "entity_id": uuid.uuid4(),
            "new_value": {"title": "Friday Collection", "amount": 5000.0, "currency": "BDT"},
            "details": "Created new income record",
            "ip_address": "127.0.0.1",
            "created_at": datetime.now(UTC) - timedelta(days=2)
        },
        {
            "masjid_id": masjid.id,
            "user_id": admin.id,
            "user_name": admin.email,
            "action": "update",
            "entity_type": "expense",
            "entity_id": uuid.uuid4(),
            "old_value": {"title": "Electricity Bill", "amount": 3000.0},
            "new_value": {"title": "Electricity Bill", "amount": 3500.0},
            "details": "Updated expense amount",
            "ip_address": "127.0.0.1",
            "created_at": datetime.now(UTC) - timedelta(days=1)
        },
        {
            "masjid_id": masjid.id,
            "user_id": admin.id,
            "user_name": admin.email,
            "action": "delete",
            "entity_type": "donor",
            "entity_id": uuid.uuid4(),
            "old_value": {"full_name": "Old Donor", "phone": "123456789"},
            "details": "Deactivated donor record",
            "ip_address": "192.168.1.50",
            "created_at": datetime.now(UTC) - timedelta(hours=12)
        }
    ]
    
    for log_data in audit_logs:
        # We don't check for existence as multiple logs can be similar
        log = AuditLog(**log_data)
        db.add(log)
        print(f"Added audit log: {log.action} on {log.entity_type} by {log.user_name}")

    db.commit()
    print("Audit log seeding completed.")

if __name__ == "__main__":
    from src.db.session import init_db
    init_db()
    with Session(engine) as session:
        seed_audit_logs(session)
