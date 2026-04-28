from sqlalchemy.orm import Session

from db.models import FailureMemory


def list_failures(db: Session, api_key_hash: str) -> list[FailureMemory]:
    return db.query(FailureMemory).filter(FailureMemory.api_key_hash == api_key_hash).order_by(FailureMemory.created_at.desc()).all()


def get_failure(db: Session, failure_id: str) -> FailureMemory | None:
    return db.query(FailureMemory).filter(FailureMemory.id == failure_id).first()
