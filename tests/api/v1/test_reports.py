import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.main import app
from src.api.dependencies import get_current_user
from src.models.user import User
from src.models.masjid import Masjid
from src.models.account import Account
from src.models.income import Income
from src.models.expense import Expense
from src.models.donor import Donor
from src.models.donation import DonationRecord
import uuid
from datetime import date, timedelta
from decimal import Decimal

# Mock User fixture
@pytest.fixture
def mock_user():
    user = User(id=uuid.uuid4(), email="testadmin@mms.app", is_active=True)
    user._token_role = "admin"
    user._token_masjid_id = uuid.uuid4()
    return user

@pytest.fixture
def auth_client(client: TestClient, mock_user: User):
    def get_current_user_override():
        return mock_user
    app.dependency_overrides[get_current_user] = get_current_user_override
    yield client
    app.dependency_overrides.clear()

def test_get_summary_stats(auth_client: TestClient, session: Session, mock_user: User):
    masjid_id = mock_user._token_masjid_id
    
    # Seed data
    masjid = Masjid(
        id=masjid_id, 
        name="Test Masjid", 
        slug="test-masjid", 
        contact_email="t@t.com",
        address="Addr",
        city="City",
        country="Country"
    )
    session.add(masjid)
    
    account = Account(id=uuid.uuid4(), masjid_id=masjid_id, account_name="Main", account_type="Cash", opening_balance=1000.0, created_by=mock_user.id)
    session.add(account)
    
    income = Income(masjid_id=masjid_id, account_id=account.id, title="I1", amount=Decimal("500.00"), category="Cat1", recorded_by=mock_user.id)
    session.add(income)
    
    expense = Expense(masjid_id=masjid_id, account_id=account.id, title="E1", amount=Decimal("200.00"), category="Cat2", recorded_by=mock_user.id)
    session.add(expense)
    
    session.commit()
    
    response = auth_client.get(f"/api/v1/reports/summary?masjid_id={masjid_id}")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_balance"]) == 1300.0
    assert float(data["this_month_income"]) == 500.0
    assert float(data["this_month_expenses"]) == 200.0

def test_get_weekly_report(auth_client: TestClient, session: Session, mock_user: User):
    masjid_id = mock_user._token_masjid_id
    today = date.today()
    start_date = today - timedelta(days=today.weekday())
    
    income = Income(masjid_id=masjid_id, title="I1", amount=Decimal("100.00"), category="C1", income_date=today, recorded_by=mock_user.id)
    session.add(income)
    session.commit()
    
    response = auth_client.get(f"/api/v1/reports/weekly?masjid_id={masjid_id}&start_date={start_date}")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_income"]) == 100.0

def test_get_monthly_report(auth_client: TestClient, session: Session, mock_user: User):
    masjid_id = mock_user._token_masjid_id
    today = date.today()
    
    income = Income(masjid_id=masjid_id, title="I1", amount=Decimal("100.00"), category="C1", income_date=today, recorded_by=mock_user.id)
    session.add(income)
    session.commit()
    
    response = auth_client.get(f"/api/v1/reports/monthly?masjid_id={masjid_id}&year={today.year}&month={today.month}")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_income"]) == 100.0
    assert "C1" in data["category_breakdown_income"]

def test_get_yearly_report(auth_client: TestClient, session: Session, mock_user: User):
    masjid_id = mock_user._token_masjid_id
    today = date.today()
    
    income = Income(masjid_id=masjid_id, title="I1", amount=Decimal("100.00"), category="C1", income_date=today, recorded_by=mock_user.id)
    session.add(income)
    session.commit()
    
    response = auth_client.get(f"/api/v1/reports/yearly?masjid_id={masjid_id}&year={today.year}")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_income"]) == 100.0
    assert len(data["monthly_data"]) == 12

def test_get_donor_report(auth_client: TestClient, session: Session, mock_user: User):
    masjid_id = mock_user._token_masjid_id
    today = date.today()
    month_str = today.strftime("%Y-%m")
    
    donor = Donor(id=uuid.uuid4(), masjid_id=masjid_id, full_name="D1", phone="1", monthly_pledge_amount=500.0, pledge_currency="USD", pledge_start_date=today, payment_method="Cash", created_by=mock_user.id)
    session.add(donor)
    session.commit()
    
    rec = DonationRecord(masjid_id=masjid_id, donor_id=donor.id, month=month_str, pledged_amount=500.0, status="pending")
    session.add(rec)
    session.commit()
    
    response = auth_client.get(f"/api/v1/reports/donors?masjid_id={masjid_id}&month={month_str}")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_pledged"]) == 500.0
    assert data["donor_details"][0]["donor_name"] == "D1"
