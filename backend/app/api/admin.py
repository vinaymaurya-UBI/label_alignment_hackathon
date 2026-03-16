from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import ActivityLog
from app.schemas.activity import ActivityLog as ActivityLogSchema, ActivityLogCreate

router = APIRouter()


@router.get("/ping")
def ping() -> dict:
    return {"status": "ok"}


@router.get("/activity", response_model=List[ActivityLogSchema])
async def get_activity_logs(
    limit: int = 50, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit)
    )
    return result.scalars().all()


@router.post("/activity", response_model=ActivityLogSchema)
async def create_activity_log(
    log_in: ActivityLogCreate, 
    db: AsyncSession = Depends(get_db)
):
    new_log = ActivityLog(**log_in.model_dump())
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log


@router.delete("/activity")
async def clear_activity_logs(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ActivityLog))
    await db.commit()
    return {"status": "ok", "message": "Activity logs cleared"}


@router.get("/analytics/summary")
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    from app.models import Drug, DrugLabel, LabelSection, RegulatoryAuthority, ActivityLog
    from sqlalchemy import func

    # 1. Basic Counts
    drug_count = (await db.execute(select(func.count(Drug.id)))).scalar() or 0
    label_count = (await db.execute(select(func.count(DrugLabel.id)))).scalar() or 0
    section_count = (await db.execute(select(func.count(LabelSection.id)))).scalar() or 0
    jurisdiction_count = (await db.execute(select(func.count(RegulatoryAuthority.id)))).scalar() or 0

    # 2. Activity Breakdown
    activity_res = await db.execute(
        select(ActivityLog.type, func.count(ActivityLog.id))
        .group_by(ActivityLog.type)
    )
    activities = {t: c for t, c in activity_res.all()}

    # 3. Jurisdictional Distribution
    jurisdiction_res = await db.execute(
        select(RegulatoryAuthority.country_code, func.count(DrugLabel.id))
        .join(DrugLabel, DrugLabel.authority_id == RegulatoryAuthority.id)
        .group_by(RegulatoryAuthority.country_code)
    )
    labels_per_country = {cc: c for cc, c in jurisdiction_res.all()}

    # 4. Synthesized "Alignment Metrics"
    # We'll calculate an "average sections per label" as a proxy for data depth
    avg_sections = section_count / label_count if label_count > 0 else 0
    
    # We'll use the number of AI reports generated as a measure of "Discrepancy Checks"
    checks_performed = activities.get("report", 0)

    return {
        "counts": {
            "drugs": drug_count,
            "labels": label_count,
            "sections": section_count,
            "jurisdictions": jurisdiction_count
        },
        "activities": activities,
        "labels_per_country": labels_per_country,
        "alignment_metrics": {
            "avg_data_depth": round(avg_sections, 1),
            "checks_performed": checks_performed,
            "alignment_score": 98.5 if checks_performed == 0 else max(75, 100 - (checks_performed * 0.5)) # Dynamic placeholder
        }
    }

