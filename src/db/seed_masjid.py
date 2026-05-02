from sqlmodel import Session, select
from src.db.session import engine
from src.models.masjid import Masjid
from src.crud.crud_masjid import masjid as crud_masjid
from src.schemas.masjid import MasjidCreate

def seed_masjids():
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
                    state="Province A",
                    country="CountryA",
                    postal_code="12345",
                    contact_email="admin@centralmasjid.com",
                    phone="+1234567890",
                    website="https://centralmasjid.com",
                    established_year=1990,
                    about="A central hub for the community.",
                    currency="USD",
                    fiscal_year_start_month="January",
                    primary_color="#2E7D32", # Green
                    accent_color="#FFD600", # Gold
                    social_media={"facebook": "https://facebook.com/centralmasjid", "twitter": "https://twitter.com/centralmasjid"},
                    is_public=True
                ),
                MasjidCreate(
                    name="Al-Noor Masjid",
                    slug="al-noor-masjid",
                    address="456 Light St",
                    city="Radiant City",
                    state="State B",
                    country="CountryB",
                    postal_code="67890",
                    contact_email="contact@alnoormasjid.com",
                    phone="+0987654321",
                    website="https://alnoormasjid.com",
                    established_year=2005,
                    about="Spreading light and knowledge.",
                    currency="BDT",
                    fiscal_year_start_month="January",
                    primary_color="#1A237E", # Blue
                    accent_color="#E91E63", # Pink
                    social_media={},
                    is_public=True
                )
            ]
            
            for data in masjid_data:
                crud_masjid.create(session=session, obj_in=data)
                print(f"Created Masjid: {data.name}")
        else:
            print("Masjid data already exists.")

if __name__ == "__main__":
    seed_masjids()
