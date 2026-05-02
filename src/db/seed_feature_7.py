import uuid
from datetime import datetime, UTC, date
from sqlmodel import Session, select
from src.db.session import engine, init_db
from src.models.masjid import Masjid
from src.models.user import User
from src.models.account import Account
from src.models.donor import Donor
from src.models.donation import DonationRecord
from src.crud import crud_donation, crud_donor

def seed_feature_7():
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

        # Get account (needed for verification)
        account = session.exec(select(Account).where(Account.masjid_id == masjid.id)).first()
        if not account:
            print("No account found for masjid. Please seed accounts first (Feature 6).")
            return

        print(f"Seeding donors for masjid: {masjid.name}")
        
        # 1. Create some Donors
        donor1_data = {
            "full_name": "Sazzad Rahman",
            "phone": "01711223344",
            "email": "sazzad@example.com",
            "monthly_pledge_amount": 50.0,
            "pledge_currency": "USD",
            "pledge_start_date": date(2026, 1, 1),
            "payment_method": "Cash",
            "notes": "Regular monthly donor"
        }
        donor2_data = {
            "full_name": "Karim Uddin",
            "phone": "01822334455",
            "email": "karim@example.com",
            "monthly_pledge_amount": 100.0,
            "pledge_currency": "USD",
            "pledge_start_date": date(2026, 2, 1),
            "payment_method": "Bank Transfer"
        }
        
        from src.schemas.donor import DonorCreate
        donor1 = crud_donor.create_donor(session, obj_in=DonorCreate(**donor1_data), masjid_id=masjid.id, user_id=user.id)
        donor2 = crud_donor.create_donor(session, obj_in=DonorCreate(**donor2_data), masjid_id=masjid.id, user_id=user.id)
        
        print(f"Donors seeded: {donor1.full_name}, {donor2.full_name}")
        
        # 2. Generate Donation Records for May 2026
        month = "2026-05"
        print(f"Generating donation records for {month}...")
        records = crud_donation.generate_monthly_donations(session, masjid_id=masjid.id, month=month)
        print(f"Generated {len(records)} records.")
        
        # 3. Verify one donation
        if records:
            record_to_verify = records[0]
            print(f"Verifying donation for donor_id: {record_to_verify.donor_id}")
            
            from src.schemas.donation import DonationVerify
            verify_in = DonationVerify(
                paid_amount=record_to_verify.pledged_amount,
                payment_date=date.today(),
                payment_method="Cash",
                account_id=account.id,
                verification_note="Received in cash after Jumu'ah"
            )
            
            verified_record = crud_donation.verify_donation_payment(
                session, 
                db_obj=record_to_verify, 
                obj_in=verify_in, 
                user_id=user.id
            )
            print(f"Donation verified. Status: {verified_record.status}, Income Record ID: {verified_record.income_record_id}")

        session.commit()
        print("Feature 7 seeding completed.")

if __name__ == "__main__":
    seed_feature_7()
