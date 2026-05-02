from typing import List, Optional
import uuid
from sqlmodel import Session, select
from src.models.audit_log import AuditLog
from src.schemas.audit_log import AuditLogCreate

class CRUDAuditLog:
    def create(self, session: Session, obj_in: AuditLogCreate) -> AuditLog:
        db_obj = AuditLog.model_validate(obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_multi_by_masjid(
        self, 
        session: Session, 
        masjid_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        statement = select(AuditLog).where(AuditLog.masjid_id == masjid_id)
        statement = statement.offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        return session.exec(statement).all()

    def get_all(
        self, 
        session: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        statement = select(AuditLog).offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        return session.exec(statement).all()

audit_log = CRUDAuditLog()
