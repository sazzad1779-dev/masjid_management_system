import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.core.config import settings
from src.models.user import User
from src.models.masjid import Masjid
from src.models.masjid_member import MasjidMember
from src.core.security import get_password_hash, create_access_token
import uuid

@pytest.fixture
def test_setup(session: Session):
    # Create test user
    user = User(email="test_acc@example.com", hashed_password=get_password_hash("password123"))
    session.add(user)
    
    # Create masjid
    masjid = Masjid(name="Test Masjid", slug="test-masjid", address="123", city="Dhaka", country="BD", contact_email="t@t.com")
    session.add(masjid)
    session.commit()
    session.refresh(user)
    session.refresh(masjid)
    
    # Create membership
    membership = MasjidMember(user_id=user.id, masjid_id=masjid.id, role="admin")
    session.add(membership)
    session.commit()
    
    # Create token
    token = create_access_token(subject=user.id, role="admin", masjid_id=masjid.id)
    
    return user, masjid, token

def test_create_account(client: TestClient, test_setup):
    user, masjid, token = test_setup
    
    account_data = {
        "account_name": "Test Bank Account",
        "account_type": "Bank",
        "bank_name": "Test Bank",
        "account_number": "987654321",
        "opening_balance": 1000.0,
        "notes": "Test account notes"
    }
    
    r = client.post(
        f"{settings.API_V1_STR}/accounts/?masjid_id={masjid.id}",
        json=account_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert r.status_code == 201
    data = r.json()
    assert data["account_name"] == "Test Bank Account"
    assert data["opening_balance"] == 1000.0
    assert data["masjid_id"] == str(masjid.id)

def test_read_accounts(client: TestClient, test_setup, session: Session):
    user, masjid, token = test_setup
    
    # Pre-create an account
    from src.models.account import Account
    acc = Account(
        masjid_id=masjid.id,
        account_name="Existing Account",
        account_type="Cash",
        opening_balance=500.0,
        created_by=user.id
    )
    session.add(acc)
    session.commit()
    
    r = client.get(
        f"{settings.API_V1_STR}/accounts/?masjid_id={masjid.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert any(a["account_name"] == "Existing Account" for a in data)

def test_get_account_balance_with_transactions(client: TestClient, test_setup, session: Session):
    user, masjid, token = test_setup
    
    # 1. Create two accounts
    from src.models.account import Account
    acc1 = Account(masjid_id=masjid.id, account_name="Acc 1", account_type="Cash", opening_balance=100.0, created_by=user.id)
    acc2 = Account(masjid_id=masjid.id, account_name="Acc 2", account_type="Bank", opening_balance=500.0, created_by=user.id)
    session.add_all([acc1, acc2])
    session.commit()
    session.refresh(acc1)
    session.refresh(acc2)
    
    # 2. Add Income to Acc 1
    from src.models.income import Income
    income = Income(masjid_id=masjid.id, account_id=acc1.id, title="I1", amount=50.0, category="C1", recorded_by=user.id)
    session.add(income)
    
    # 3. Add Expense to Acc 1
    from src.models.expense import Expense
    expense = Expense(masjid_id=masjid.id, account_id=acc1.id, title="E1", amount=20.0, category="C2", recorded_by=user.id)
    session.add(expense)
    
    # 4. Transfer Acc 1 to Acc 2
    from src.models.account import AccountTransfer
    transfer = AccountTransfer(masjid_id=masjid.id, from_account_id=acc1.id, to_account_id=acc2.id, amount=30.0, currency="USD", recorded_by=user.id)
    session.add(transfer)
    
    session.commit()
    
    # Final Balance of Acc 1 should be: 100 (opening) + 50 (income) - 20 (expense) - 30 (transfer out) = 100
    r = client.get(
        f"{settings.API_V1_STR}/accounts/{acc1.id}/balance?masjid_id={masjid.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    assert r.json()["current_balance"] == 100.0
    
    # Final Balance of Acc 2 should be: 500 (opening) + 30 (transfer in) = 530
    r = client.get(
        f"{settings.API_V1_STR}/accounts/{acc2.id}/balance?masjid_id={masjid.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    assert r.json()["current_balance"] == 530.0

def test_create_transfer_api(client: TestClient, test_setup, session: Session):
    user, masjid, token = test_setup
    
    # Create two accounts
    from src.models.account import Account
    acc1 = Account(masjid_id=masjid.id, account_name="Source", account_type="Cash", opening_balance=500.0, created_by=user.id)
    acc2 = Account(masjid_id=masjid.id, account_name="Dest", account_type="Bank", opening_balance=0.0, created_by=user.id)
    session.add_all([acc1, acc2])
    session.commit()
    session.refresh(acc1)
    session.refresh(acc2)
    
    transfer_data = {
        "from_account_id": str(acc1.id),
        "to_account_id": str(acc2.id),
        "amount": 150.0,
        "currency": "USD",
        "notes": "API Transfer"
    }
    
    r = client.post(
        f"{settings.API_V1_STR}/accounts/transfer?masjid_id={masjid.id}",
        json=transfer_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert r.status_code == 201
    data = r.json()
    assert data["amount"] == 150.0
    assert data["from_account_id"] == str(acc1.id)
    assert data["to_account_id"] == str(acc2.id)
