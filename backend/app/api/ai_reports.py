"""
AI report endpoints: SSE streaming generation + DOCX download.
"""
import io
import json
import re
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.ai_service import get_ai_generator

router = APIRouter()


# ---------------------------------------------------------------------------
# SSE streaming report generation
# ---------------------------------------------------------------------------

async def _stream(db: AsyncSession, drug_id: str) -> AsyncGenerator[bytes, None]:
    def evt(data: dict) -> bytes:
        return b"data: " + json.dumps(data).encode() + b"\n\n"

    yield evt({"status": "starting", "progress": 0, "message": "Initializing..."})

    ai = get_ai_generator()
    if ai is None:
        yield evt({"status": "error", "message": "AI service not configured (missing ANTHROPIC_API_KEY)"})
        return

    try:
        yield evt({"status": "generating", "progress": 30, "message": "Generating AI-powered analysis..."})
        report_md = await ai.generate_report(db, drug_id)
        yield evt({"status": "complete", "progress": 100, "message": "Done!", "report": report_md})
    except ValueError as exc:
        yield evt({"status": "error", "message": str(exc)})
    except Exception as exc:
        yield evt({"status": "error", "message": f"AI generation failed: {exc}"})


@router.post("/generate-report/{drug_id}")
async def generate_report_stream(drug_id: str, db: AsyncSession = Depends(get_db)):
    return StreamingResponse(
        _stream(db, drug_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# DOCX download
# ---------------------------------------------------------------------------

class DocxRequest(BaseModel):
    report: str


def _markdown_to_docx(markdown: str) -> bytes:
    from docx import Document
    from docx.shared import Pt, RGBColor

    doc = Document()

    # Style the default paragraph font
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#### "):
            doc.add_heading(stripped[5:], level=4)
        elif stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            para = doc.add_paragraph(stripped[2:], style="List Bullet")
        elif stripped.startswith("---"):
            doc.add_paragraph("─" * 60)
        elif stripped == "":
            doc.add_paragraph("")
        else:
            # Strip inline bold/italic markers for plain text
            clean = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
            clean = re.sub(r"\*(.+?)\*", r"\1", clean)
            doc.add_paragraph(clean)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@router.post("/download-docx/{drug_id}")
async def download_docx(drug_id: str, body: DocxRequest):
    docx_bytes = _markdown_to_docx(body.report)
    filename = f"drug_report_{drug_id}.docx"
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# AI status
# ---------------------------------------------------------------------------

@router.get("/status")
async def ai_status():
    ai = get_ai_generator()
    if ai is None:
        return {"status": "error", "available": False, "message": "ANTHROPIC_API_KEY not configured"}
    return {"status": "available", "available": True, "provider": "Anthropic Claude 3.5 Sonnet"}
