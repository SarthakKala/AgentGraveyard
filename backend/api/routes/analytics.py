from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import FailureMemory, SuccessMemory

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def overview(api_key_hash: str, db: Session = Depends(get_db)):
    total_failures = db.query(FailureMemory).filter(FailureMemory.api_key_hash == api_key_hash).count()
    total_successes = db.query(SuccessMemory).filter(SuccessMemory.api_key_hash == api_key_hash).count()
    healed = (
        db.query(FailureMemory)
        .filter(FailureMemory.api_key_hash == api_key_hash, FailureMemory.self_heal_succeeded.is_(True))
        .count()
    )
    category = (
        db.query(FailureMemory.failure_category, func.count(FailureMemory.id).label("c"))
        .filter(FailureMemory.api_key_hash == api_key_hash)
        .group_by(FailureMemory.failure_category)
        .order_by(func.count(FailureMemory.id).desc())
        .first()
    )
    most_agent = (
        db.query(FailureMemory.agent_name, func.count(FailureMemory.id).label("c"))
        .filter(FailureMemory.api_key_hash == api_key_hash)
        .group_by(FailureMemory.agent_name)
        .order_by(func.count(FailureMemory.id).desc())
        .first()
    )
    week_start = datetime.utcnow() - timedelta(days=7)
    failures_this_week = (
        db.query(FailureMemory)
        .filter(FailureMemory.api_key_hash == api_key_hash, FailureMemory.created_at >= week_start)
        .count()
    )
    return {
        "total_failures": total_failures,
        "total_successes": total_successes,
        "self_heal_success_rate": (healed / total_failures) if total_failures else 0.0,
        "most_common_failure_category": category[0] if category else None,
        "most_failing_agent": most_agent[0] if most_agent else None,
        "failures_this_week": failures_this_week,
        "wisdom_injections_count": 0,
    }


@router.get("/failure-categories")
def failure_categories(api_key_hash: str, db: Session = Depends(get_db)):
    rows = (
        db.query(FailureMemory.failure_category, func.count(FailureMemory.id).label("count"))
        .filter(FailureMemory.api_key_hash == api_key_hash)
        .group_by(FailureMemory.failure_category)
        .all()
    )
    return [{"category": r[0], "count": r[1]} for r in rows]


@router.get("/timeline")
def timeline(api_key_hash: str, db: Session = Depends(get_db)):
    start = datetime.utcnow() - timedelta(days=30)
    rows = (
        db.query(func.date(FailureMemory.created_at).label("day"), func.count(FailureMemory.id))
        .filter(FailureMemory.api_key_hash == api_key_hash, FailureMemory.created_at >= start)
        .group_by(func.date(FailureMemory.created_at))
        .all()
    )
    return [{"day": str(r[0]), "failures": r[1]} for r in rows]


@router.get("/agents")
def agents(api_key_hash: str, db: Session = Depends(get_db)):
    rows = (
        db.query(FailureMemory.agent_name, func.count(FailureMemory.id))
        .filter(FailureMemory.api_key_hash == api_key_hash)
        .group_by(FailureMemory.agent_name)
        .order_by(func.count(FailureMemory.id).desc())
        .all()
    )
    return [{"agent_name": r[0], "failures": r[1]} for r in rows]
