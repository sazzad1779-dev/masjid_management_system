from sqlmodel import Session, select
from src.db.session import engine, init_db
from src.models.masjid import Masjid
from src.crud.crud_masjid import masjid as crud_masjid
from src.schemas.masjid import MasjidCreate
from src.models.user import User
from src.core.security import get_password_hash

def seed_data():
    # Recreate tables with new schema
    init_db()
    
    with Session(engine) as session:
        # Seed Masjid Data
        if crud_masjid.count_all(session) == 0:
            print("Seeding initial masjid data...")
            masjid_data = [
                MasjidCreate(
                    name="Central Masjid",
                    slug="central-masjid",
                    address="123 Main St",
                    city="Capital City",
                    country="CountryA",
                    contact_email="admin@centralmasjid.com",
                    phone="+1234567890",
                    currency="USD",
                    fiscal_year_start="January",
                    primary_color="#2E7D32", # Green
                    secondary_color="#FFD600", # Gold
                    social_media={"facebook": "https://facebook.com/centralmasjid", "twitter": "https://twitter.com/centralmasjid"},
                    is_public=True
                )
            ]
            
            for data in masjid_data:
                crud_masjid.create(session=session, obj_in=data)
                print(f"Created Masjid: {data.name}")

        # Seed User Data
        statement = select(User).where(User.email == "admin@masjid.com")
        existing_user = session.exec(statement).first()
        
        if not existing_user:
            print("Seeding superadmin user...")
            super_admin = User(
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

if __name__ == "__main__":
    import os
    # Delete masjid.db to ensure schema update
    if os.path.exists("masjid.db"):
        os.remove("masjid.db")
        print("Deleted old masjid.db")
    seed_data()
