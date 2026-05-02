from typing import Optional, Dict, Any
from sqlmodel import Session
from src.crud import audit_log as audit_log_crud
from src.schemas.audit_log import AuditLogCreate
import uuid

class AuditLogService:
    @staticmethod
    def log_action(
        db: Session,
        user_id: uuid.UUID,
        user_name: str,
        action: str,
        entity_type: str,
        masjid_id: Optional[uuid.UUID] = None,
        entity_id: Optional[uuid.UUID] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        import json
        
        # Ensure values are JSON serializable (SQLAlchemy SQLite JSON col needs this for complex types)
        def serialize_dict(d: Optional[Dict]) -> Optional[Dict]:
            if d is None:
                return None
            return json.loads(json.dumps(d, default=str))

        audit_log_in = AuditLogCreate(
            masjid_id=masjid_id,
            user_id=user_id,
            user_name=user_name,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=serialize_dict(old_value),
            new_value=serialize_dict(new_value),
            ip_address=ip_address,
            user_agent=user_agent
        )
        return audit_log_crud.audit_log.create(db, obj_in=audit_log_in)
