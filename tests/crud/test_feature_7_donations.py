import pytest
from sqlmodel import Session
from src.crud import crud_donor, crud_donation, crud_account
from src.schemas.donor import DonorCreate
from src.schemas.donation import DonationVerify, DonationRecordUpdate
from src.schemas.account import AccountCreate
from src.models.masjid import Masjid
from src.models.user import User
from datetime import date, UTC, datetime
import uuid

def setup_test_data(session: Session):
    masjid = Masjid(name="Test Masjid", slug="test-masjid", address="Test", city="Test", country="Test", contact_email="test@test.com")
    session.add(masjid)
    session.commit()
    session.refresh(masjid)
    
    superuser = User(email="admin@test.com", hashed_password="hash", role="super_admin", is_active=True)
    session.add(superuser)
    session.commit()
    session.refresh(superuser)
    
    account_in = AccountCreate(
        account_name="Test Cash",
        account_type="Cash",
        opening_balance=1000.0
    )
    account = crud_account.create_account(session, obj_in=account_in, masjid_id=masjid.id, user_id=superuser.id)
    
    return masjid, superuser, account

def test_create_donor(session: Session):
    masjid, superuser, _ = setup_test_data(session)
    donor_in = DonorCreate(
        full_name="Test Donor",
        phone="01711223344",
        email="donor@test.com",
        monthly_pledge_amount=100.0,
        pledge_start_date=date.today(),
        payment_method="Cash"
    )
    donor = crud_donor.create_donor(session, obj_in=donor_in, masjid_id=masjid.id, user_id=superuser.id)
    assert donor.full_name == "Test Donor"
    assert donor.monthly_pledge_amount == 100.0
    assert donor.masjid_id == masjid.id

def test_generate_monthly_donations(session: Session):
    masjid, superuser, _ = setup_test_data(session)
    donor_in = DonorCreate(
        full_name="Monthly Donor",
        phone="01711223344",
        monthly_pledge_amount=100.0,
        pledge_start_date=date.today(),
        payment_method="Cash"
    )
    crud_donor.create_donor(session, obj_in=donor_in, masjid_id=masjid.id, user_id=superuser.id)
    
    month = "2026-05"
    records = crud_donation.generate_monthly_donations(session, masjid_id=masjid.id, month=month)
    assert len(records) == 1
    assert records[0].month == month
    assert records[0].pledged_amount == 100.0
    assert records[0].status == "pending"

def test_verify_donation_payment(session: Session):
    masjid, superuser, account = setup_test_data(session)
    donor_in = DonorCreate(
        full_name="Verifying Donor",
        phone="01711223344",
        monthly_pledge_amount=100.0,
        pledge_start_date=date.today(),
        payment_method="Cash"
    )
    donor = crud_donor.create_donor(session, obj_in=donor_in, masjid_id=masjid.id, user_id=superuser.id)
    
    month = "2026-05"
    records = crud_donation.generate_monthly_donations(session, masjid_id=masjid.id, month=month)
    record = records[0]
    
    verify_in = DonationVerify(
        paid_amount=100.0,
        payment_date=date.today(),
        payment_method="Cash",
        account_id=account.id,
        verification_note="Checked"
    )
    
    verified_record = crud_donation.verify_donation_payment(
        session, 
        db_obj=record, 
        obj_in=verify_in, 
        user_id=superuser.id
    )
    
    assert verified_record.status == "paid"
    assert verified_record.paid_amount == 100.0
    assert verified_record.income_record_id is not None
    
    from src.models.income import Income
    income = session.get(Income, verified_record.income_record_id)
    assert income.amount == 100.0
    assert income.category == "Monthly Donation"
    assert income.donor_id == donor.id
