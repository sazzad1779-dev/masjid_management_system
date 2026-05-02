from sqlmodel import Session, select
from src.models.masjid import Masjid
from src.schemas.masjid import MasjidCreate, MasjidUpdate
import uuid

class CRUDMasjid:
    def create(self, session: Session, obj_in: MasjidCreate) -> Masjid:
        db_obj = Masjid.model_validate(obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get(self, session: Session, id: uuid.UUID) -> Masjid | None:
        return session.get(Masjid, id)

    def update(self, session: Session, db_obj: Masjid, obj_in: MasjidUpdate) -> Masjid:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def count_all(self, session: Session) -> int:
        return len(session.exec(select(Masjid)).all())

masjid = CRUDMasjid()
