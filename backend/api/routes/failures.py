from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import FailureMemory
from memory.pinecone_client import delete_failure, update_failure_metadata

router = APIRouter(prefix="/api/failures", tags=["failures"])


@router.get("")
def get_failures(
    api_key_hash: str,
    failure_category: str | None = None,
    agent_name: str | None = None,
    resolved: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(FailureMemory).filter(FailureMemory.api_key_hash == api_key_hash)
    if failure_category:
        query = query.filter(FailureMemory.failure_category == failure_category)
    if agent_name:
        query = query.filter(FailureMemory.agent_name == agent_name)
    if resolved is not None:
        query = query.filter(FailureMemory.resolved_eventually == resolved)
    total = query.count()
    rows = query.order_by(FailureMemory.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": rows, "total": total, "page": page, "page_size": page_size}


@router.get("/community")
def get_community_failures(db: Session = Depends(get_db)):
    rows = (
        db.query(FailureMemory)
        .filter(FailureMemory.is_community_shared.is_(True))
        .order_by(FailureMemory.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": row.id,
            "agent_name": row.agent_name,
            "task_description": row.task_description,
            "is_community_shared": bool(row.is_community_shared),
            "failure_category": row.failure_category,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


@router.get("/{failure_id}")
def get_failure(failure_id: str, db: Session = Depends(get_db)):
    failure = db.query(FailureMemory).filter(FailureMemory.id == failure_id).first()
    if not failure:
        raise HTTPException(status_code=404, detail="Failure not found")
    return failure


@router.patch("/{failure_id}")
def update_failure(failure_id: str, payload: dict, db: Session = Depends(get_db)):
    failure = db.query(FailureMemory).filter(FailureMemory.id == failure_id).first()
    if not failure:
        raise HTTPException(status_code=404, detail="Failure not found")
    for key in ["resolved_eventually", "resolution_description", "is_community_shared"]:
        if key in payload:
            setattr(failure, key, payload[key])
    db.commit()
    update_failure_metadata(failure_id, payload)
    return failure


@router.delete("/{failure_id}")
def remove_failure(failure_id: str, db: Session = Depends(get_db)):
    failure = db.query(FailureMemory).filter(FailureMemory.id == failure_id).first()
    if not failure:
        raise HTTPException(status_code=404, detail="Failure not found")
    db.delete(failure)
    db.commit()
    delete_failure(failure_id)
    return {"ok": True}
