"""
Drug endpoints: list, detail, compare, sections.
Mirrors the response shape of the original app/api/drugs.py.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Drug, DrugLabel, LabelSection, RegulatoryAuthority

router = APIRouter()

DATA_SOURCES: Dict[str, Dict[str, str]] = {
    "US": {"name": "FDA openFDA API", "type": "API", "url": "https://open.fda.gov/"},
    "JP": {"name": "PMDA Website", "type": "SCRAPER", "url": "https://www.pmda.go.jp/"},
    "IN": {"name": "CDSCO Portal", "type": "SCRAPER", "url": "https://cdsco.gov.in/"},
    "GB": {"name": "MHRA/EMC Database", "type": "SCRAPER", "url": "https://www.medicines.org.uk/"},
    "CA": {"name": "Health Canada DPD", "type": "SCRAPER", "url": "https://www.canada.ca/"},
    "EU": {"name": "European Medicines Agency", "type": "SCRAPER", "url": "https://www.ema.europa.eu/"},
    "AU": {"name": "Therapeutic Goods Administration", "type": "SCRAPER", "url": "https://www.tga.gov.au/"},
}


def _ds(country_code: str) -> Dict[str, str]:
    return DATA_SOURCES.get(country_code, {"name": "Unknown Source", "type": "UNKNOWN", "url": ""})


@router.get("/")
async def list_drugs(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
    manufacturer: Optional[str] = Query(default=None),
    country: Optional[str] = Query(default=None),
) -> JSONResponse:
    stmt = select(Drug)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(Drug.brand_name.ilike(pattern) | Drug.generic_name.ilike(pattern))
    if manufacturer:
        stmt = stmt.where(Drug.manufacturer.ilike(f"%{manufacturer}%"))

    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total: int = count_result.scalar() or 0

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    drugs = result.scalars().all()

    drug_list: List[Dict[str, Any]] = []
    for drug in drugs:
        # Fetch country codes for this drug
        cc_stmt = (
            select(func.distinct(RegulatoryAuthority.country_code))
            .join(DrugLabel, DrugLabel.authority_id == RegulatoryAuthority.id)
            .where(DrugLabel.drug_id == drug.id)
        )
        if country:
            cc_stmt = cc_stmt.where(RegulatoryAuthority.country_code == country.upper())
        cc_result = await db.execute(cc_stmt)
        country_codes = [r[0] for r in cc_result.all()]

        label_count = len(country_codes)
        drug_list.append(
            {
                "id": drug.id,
                "generic_name": drug.generic_name,
                "brand_name": drug.brand_name,
                "manufacturer": drug.manufacturer,
                "active_ingredient": drug.active_ingredient,
                "therapeutic_area": drug.therapeutic_area,
                "country_codes": country_codes,
                "label_count": label_count,
            }
        )

    return JSONResponse({"drugs": drug_list, "total": total, "limit": limit, "offset": offset})


@router.get("/manufacturers")
async def list_manufacturers(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    result = await db.execute(
        select(func.distinct(Drug.manufacturer)).where(Drug.manufacturer.isnot(None)).order_by(Drug.manufacturer)
    )
    manufacturers = [r[0] for r in result.all() if r[0]]
    return JSONResponse({"manufacturers": manufacturers})


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    drug_count_result = await db.execute(select(func.count(Drug.id)))
    drug_count: int = drug_count_result.scalar() or 0

    label_count_result = await db.execute(select(func.count(DrugLabel.id)))
    label_count: int = label_count_result.scalar() or 0

    section_count_result = await db.execute(select(func.count(LabelSection.id)))
    section_count: int = section_count_result.scalar() or 0

    country_count_result = await db.execute(
        select(func.count(func.distinct(RegulatoryAuthority.country_code)))
    )
    country_count: int = country_count_result.scalar() or 0

    return JSONResponse(
        {
            "drugs": drug_count,
            "labels": label_count,
            "sections": section_count,
            "countries": country_count,
        }
    )


@router.get("/{drug_id}")
async def get_drug_detail(drug_id: str, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    drug_result = await db.execute(select(Drug).where(Drug.id == drug_id))
    drug = drug_result.scalar_one_or_none()
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    labels_result = await db.execute(
        select(DrugLabel, RegulatoryAuthority)
        .join(RegulatoryAuthority, DrugLabel.authority_id == RegulatoryAuthority.id)
        .where(DrugLabel.drug_id == drug_id)
    )

    labels: List[Dict[str, Any]] = []
    for label, authority in labels_result.all():
        sections_result = await db.execute(
            select(LabelSection)
            .where(LabelSection.label_id == label.id)
            .order_by(LabelSection.section_order)
        )
        sections = [
            {
                "id": s.id,
                "section_name": s.section_name,
                "section_order": s.section_order,
                "content": s.content,
            }
            for s in sections_result.scalars().all()
        ]
        ds = _ds(authority.country_code)
        labels.append(
            {
                "id": label.id,
                "authority": authority.country_name,
                "country_code": authority.country_code,
                "label_type": label.label_type,
                "effective_date": label.effective_date.isoformat() if label.effective_date else None,
                "sections": sections,
                "data_source_type": ds["type"],
                "data_source_name": ds["name"],
                "data_source_url": ds["url"],
            }
        )

    return JSONResponse(
        {
            "id": drug.id,
            "generic_name": drug.generic_name,
            "brand_name": drug.brand_name,
            "manufacturer": drug.manufacturer,
            "active_ingredient": drug.active_ingredient,
            "therapeutic_area": drug.therapeutic_area,
            "labels": labels,
        }
    )


@router.get("/{drug_id}/compare")
async def compare_drug_labels(drug_id: str, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    drug_result = await db.execute(select(Drug).where(Drug.id == drug_id))
    drug = drug_result.scalar_one_or_none()
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    labels_result = await db.execute(
        select(DrugLabel, RegulatoryAuthority)
        .join(RegulatoryAuthority, DrugLabel.authority_id == RegulatoryAuthority.id)
        .where(DrugLabel.drug_id == drug_id)
    )
    label_by_id: Dict[str, tuple] = {}
    for label, authority in labels_result.all():
        label_by_id[label.id] = (label, authority)

    sections_result = await db.execute(
        select(LabelSection).where(LabelSection.label_id.in_(label_by_id.keys()))
    )

    by_heading: Dict[str, list] = {}
    for s in sections_result.scalars().all():
        label, authority = label_by_id[s.label_id]
        by_heading.setdefault(s.section_name, []).append(
            {
                "country_code": authority.country_code,
                "country_name": authority.country_name,
                "label_id": label.id,
                "section_id": s.id,
                "content": s.content,
            }
        )

    comparisons = [
        {"section_heading": heading, "entries": entries}
        for heading, entries in by_heading.items()
    ]

    name = drug.brand_name or drug.generic_name or ""
    return JSONResponse(
        {
            "drug_id": drug.id,
            "drug_name": name,
            "generic_name": drug.generic_name,
            "brand_name": drug.brand_name,
            "manufacturer": drug.manufacturer,
            "comparisons": comparisons,
        }
    )
