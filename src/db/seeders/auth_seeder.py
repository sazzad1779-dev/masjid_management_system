import uuid
from sqlmodel import Session, select
from src.core.security import get_password_hash
from src.models.user import User
from src.models.masjid import Masjid
from src.models.masjid_member import MasjidMember
from src.db.session import engine

def seed_auth(db: Session):
    print("Seeding Authentication & Authorization (Feature 2)...")
    
    # 1. Create Super Admin
    super_admin = db.exec(select(User).where(User.email == "superadmin@mms.app")).first()
    if not super_admin:
        super_admin = User(
            email="superadmin@mms.app",
            hashed_password=get_password_hash("superpassword123"),
            is_active=True
        )
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        print(f"Created Super Admin: {super_admin.email}")
    
    # 2. Create Masjids if they don't exist
    masjid_al_noor = db.exec(select(Masjid).where(Masjid.slug == "al-noor")).first()
    if not masjid_al_noor:
        masjid_al_noor = Masjid(
            name="Masjid Al-Noor",
            slug="al-noor",
            address="123 Street",
            city="Dhaka",
            country="Bangladesh",
            contact_email="contact@alnoor.org"
        )
        db.add(masjid_al_noor)
        
    masjid_al_huda = db.exec(select(Masjid).where(Masjid.slug == "al-huda")).first()
    if not masjid_al_huda:
        masjid_al_huda = Masjid(
            name="Masjid Al-Huda",
            slug="al-huda",
            address="456 Avenue",
            city="Chittagong",
            country="Bangladesh",
            contact_email="contact@alhuda.org"
        )
        db.add(masjid_al_huda)
    
    db.commit()
    db.refresh(masjid_al_noor)
    db.refresh(masjid_al_huda)

    # 3. Create a Masjid Admin who belongs to both masjids
    masjid_admin = db.exec(select(User).where(User.email == "admin@mms.app")).first()
    if not masjid_admin:
        masjid_admin = User(
            email="admin@mms.app",
            hashed_password=get_password_hash("adminpassword123"),
            is_active=True
        )
        db.add(masjid_admin)
        db.commit()
        db.refresh(masjid_admin)
        print(f"Created Masjid Admin: {masjid_admin.email}")

    # Add memberships
    for m_id, role in [(masjid_al_noor.id, "admin"), (masjid_al_huda.id, "committee")]:
        membership = db.exec(select(MasjidMember).where(
            MasjidMember.user_id == masjid_admin.id,
            MasjidMember.masjid_id == m_id
        )).first()
        if not membership:
            membership = MasjidMember(
                user_id=masjid_admin.id,
                masjid_id=m_id,
                role=role
            )
            db.add(membership)
            print(f"Added {masjid_admin.email} to {m_id} as {role}")

    # 4. Create a Regular User
    regular_user = db.exec(select(User).where(User.email == "user@mms.app")).first()
    if not regular_user:
        regular_user = User(
            email="user@mms.app",
            hashed_password=get_password_hash("userpassword123"),
            is_active=True
        )
        db.add(regular_user)
        db.commit()
        db.refresh(regular_user)
        print(f"Created Regular User: {regular_user.email}")
        
        # Add to one masjid
        db.add(MasjidMember(user_id=regular_user.id, masjid_id=masjid_al_noor.id, role="viewer"))

    db.commit()
    print("Authentication seeding completed.")

if __name__ == "__main__":
    from src.db.session import init_db
    init_db()
    with Session(engine) as session:
        seed_auth(session)
