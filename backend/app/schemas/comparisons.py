from typing import List, Optional

from pydantic import BaseModel


class SectionComparison(BaseModel):
    heading: str
    country_code: str
    content: str


class LabelComparison(BaseModel):
    drug_id: int
    section_heading: str
    sections: List[SectionComparison]
    discrepancy_summary: Optional[str] = None

