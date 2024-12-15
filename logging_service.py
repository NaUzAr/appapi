# app/logging_service.py

from .schemas import ActivityLogCreate, ActivityLogResponse
from .models import ActivityLog
from sqlalchemy.orm import Session

def log_activity(db: Session, log: ActivityLogCreate, user_id: int) -> ActivityLogResponse:
    activity_log = ActivityLog(
        action=log.action,
        user_id=user_id
    )
    db.add(activity_log)
    db.commit()
    db.refresh(activity_log)
    return ActivityLogResponse(
        id=activity_log.id,
        user_id=activity_log.user_id,
        action=activity_log.action,
        timestamp=activity_log.timestamp
    )
