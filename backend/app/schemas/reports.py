from pydantic import BaseModel


class ReportRequest(BaseModel):
    drug_id: int


class ReportChunk(BaseModel):
    status: str
    progress: int | None = None
    report_markdown: str | None = None

