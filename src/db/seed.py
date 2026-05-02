from sqlmodel import Session, select
from src.db.session import engine, init_db
from src.models.user import User
from src.core.security import get_password_hash
from src.db.seed_masjid import seed_masjids
from src.db.seed_income import seed_income

def seed_data():
    # Recreate tables with new schema
    init_db()
    
    # Seed Masjid Data
    seed_masjids()

    with Session(engine) as session:
        # Seed User Data
        statement = select(User).where(User.role == "super_admin")
        existing_user = session.exec(statement).first()
        
        if not existing_user:
            print("Seeding superadmin user...")
            super_admin = User(
                full_name="Super Admin",
                email="admin@masjid.com",
                hashed_password=get_password_hash("admin123"),
                role="super_admin",
                is_active=True
            )
            session.add(super_admin)
            session.commit()
            print("Successfully seeded superadmin user.")
        else:
            print("Superadmin user already exists.")
    
    # Seed Income Data
    seed_income()

if __name__ == "__main__":
    import os
    # Delete masjid.db to ensure schema update
    if os.path.exists("masjid.db"):
        os.remove("masjid.db")
        print("Deleted old masjid.db")
    seed_data()
