from sqlmodel import Session, select
from src.db.session import engine, init_db
from src.models.masjid import Masjid
import uuid

def seed_feature_3():
    # Ensure tables are created with new schema
    init_db()
    with Session(engine) as session:
        # Check if Al-Noor Masjid exists
        statement = select(Masjid).where(Masjid.slug == "al-noor")
        masjid = session.exec(statement).first()
        
        if not masjid:
            print("Creating Al-Noor Masjid for Feature 3...")
            masjid = Masjid(
                name="Al-Noor Islamic Center",
                slug="al-noor",
                address="123 Faith Street",
                city="Dhaka",
                state="Dhaka",
                country="Bangladesh",
                postal_code="1200",
                contact_email="contact@alnoor.org",
                phone="+880123456789",
                website="https://alnoor-masjid.org",
                established_year=1995,
                about="A community center serving the local area with daily prayers and education.",
                logo_url="https://alnoor.org/logo.png",
                cover_url="https://alnoor.org/cover.jpg",
                currency="BDT",
                fiscal_year_start_month="July",
                primary_color="#1b5e20",
                accent_color="#8bc34a",
                friday_jumuah_time="1:30 PM",
                notification_settings={
                    "email_alerts": True,
                    "sms_alerts": False,
                    "monthly_report_digest": True
                },
                default_categories={
                    "income": ["Friday Collection", "Zakat", "Sadaqah", "Rental"],
                    "expense": ["Utilities", "Salary", "Maintenance", "Events"]
                },
                social_media={
                    "facebook": "https://facebook.com/alnoor",
                    "youtube": "https://youtube.com/alnoor"
                }
            )
            session.add(masjid)
            session.commit()
            session.refresh(masjid)
            print(f"Successfully seeded Al-Noor Masjid with ID: {masjid.id}")
        else:
            # Update existing masjid with new fields
            print("Updating Al-Noor Masjid with Feature 3 fields...")
            masjid.friday_jumuah_time = "1:30 PM"
            masjid.notification_settings = {
                "email_alerts": True,
                "sms_alerts": False,
                "monthly_report_digest": True
            }
            masjid.default_categories = {
                "income": ["Friday Collection", "Zakat", "Sadaqah", "Rental"],
                "expense": ["Utilities", "Salary", "Maintenance", "Events"]
            }
            session.add(masjid)
            session.commit()
            print("Successfully updated Al-Noor Masjid.")

if __name__ == "__main__":
    seed_feature_3()
