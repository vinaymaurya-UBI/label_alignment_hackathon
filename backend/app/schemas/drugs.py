from typing import List, Optional

from pydantic import BaseModel


class Section(BaseModel):
    id: str
    order_index: int
    heading: str
    content: str


class Label(BaseModel):
    id: str
    country_code: str
    title: str
    section_count: int
    sections: List[Section] = []


class DrugSummary(BaseModel):
    id: str
    name: str
    country_codes: List[str]


class DrugDetail(BaseModel):
    id: str
    name: str
    labels: List[Label]


class DrugQuery(BaseModel):
    search: Optional[str] = None
    country: Optional[str] = None
    limit: int = 20
    offset: int = 0

