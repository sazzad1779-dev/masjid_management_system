import pytest
from sqlmodel import Session
from src.crud import crud_income
from src.schemas.income import IncomeCreate, IncomeUpdate
from src.models.masjid import Masjid
from src.models.user import User
from decimal import Decimal
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
    return masjid, superuser

def test_create_income(session: Session):
    masjid, superuser = setup_test_data(session)
    income_in = IncomeCreate(
        masjid_id=masjid.id,
        title="Test Income",
        amount=Decimal("500.00"),
        category="Sadaqah",
        income_date=date.today(),
        recorded_by=superuser.id
    )
    income = crud_income.income.create(session=session, obj_in=income_in)
    assert income.title == "Test Income"
    assert income.amount == Decimal("500.00")
    assert income.masjid_id == masjid.id

def test_get_income(session: Session):
    masjid, superuser = setup_test_data(session)
    income_in = IncomeCreate(
        masjid_id=masjid.id,
        title="Test Income",
        amount=Decimal("500.00"),
        category="Sadaqah",
        income_date=date.today(),
        recorded_by=superuser.id
    )
    income = crud_income.income.create(session=session, obj_in=income_in)
    stored_income = crud_income.income.get(session=session, id=income.id)
    assert stored_income
    assert stored_income.id == income.id
    assert stored_income.title == income.title

def test_update_income(session: Session):
    masjid, superuser = setup_test_data(session)
    income_in = IncomeCreate(
        masjid_id=masjid.id,
        title="Test Income",
        amount=Decimal("500.00"),
        category="Sadaqah",
        income_date=date.today(),
        recorded_by=superuser.id
    )
    income = crud_income.income.create(session=session, obj_in=income_in)
    income_update = IncomeUpdate(title="Updated Title", amount=Decimal("600.00"))
    updated_income = crud_income.income.update(session=session, db_obj=income, obj_in=income_update)
    assert updated_income.title == "Updated Title"
    assert updated_income.amount == Decimal("600.00")

def test_delete_income(session: Session):
    masjid, superuser = setup_test_data(session)
    income_in = IncomeCreate(
        masjid_id=masjid.id,
        title="Test Income",
        amount=Decimal("500.00"),
        category="Sadaqah",
        income_date=date.today(),
        recorded_by=superuser.id
    )
    income = crud_income.income.create(session=session, obj_in=income_in)
    deleted_income = crud_income.income.remove(session=session, id=income.id, deleted_by=superuser.id)
    assert deleted_income.is_deleted is True
    assert deleted_income.deleted_by == superuser.id
    assert deleted_income.deleted_at is not None

def test_get_multi_by_masjid(session: Session):
    masjid, superuser = setup_test_data(session)
    income_in = IncomeCreate(
        masjid_id=masjid.id,
        title="Test Income 1",
        amount=Decimal("100.00"),
        category="Zakat",
        income_date=date.today(),
        recorded_by=superuser.id
    )
    crud_income.income.create(session=session, obj_in=income_in)
    
    incomes = crud_income.income.get_multi_by_masjid(session=session, masjid_id=masjid.id)
    assert len(incomes) > 0
    assert incomes[0].masjid_id == masjid.id

def test_get_weekly_summary(session: Session):
    masjid, superuser = setup_test_data(session)
    today = date.today()
    # Find the Sunday of the current week (assuming Monday is start)
    # Actually, let's just use today and the next 6 days
    income_in = IncomeCreate(
        masjid_id=masjid.id,
        title="Weekly Income",
        amount=Decimal("1000.00"),
        category="Friday Jumu'ah Collection",
        income_date=today,
        recorded_by=superuser.id
    )
    crud_income.income.create(session=session, obj_in=income_in)
    
    summary = crud_income.income.get_weekly_summary(session=session, masjid_id=masjid.id, start_date=today)
    assert summary["total_income"] >= Decimal("1000.00")
