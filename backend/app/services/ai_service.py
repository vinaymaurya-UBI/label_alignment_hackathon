"""
AI report generation using Anthropic Claude.
Ported from the original app/services/ai_service.py.
"""
import asyncio
from datetime import datetime
from typing import Any, Dict

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Drug, DrugLabel, LabelSection, RegulatoryAuthority


class AIReportGenerator:
    def __init__(self) -> None:
        raw = settings.ANTHROPIC_API_KEY
        self.api_key = (raw or "").strip() or None
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        base_url = settings.ANTHROPIC_BASE_URL
        if base_url:
            self.client = anthropic.Anthropic(api_key=self.api_key, base_url=base_url)
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    async def gather_drug_data(self, db: AsyncSession, drug_id: str) -> Dict[str, Any]:
        drug_result = await db.execute(select(Drug).where(Drug.id == drug_id))
        drug = drug_result.scalar_one_or_none()
        if not drug:
            raise ValueError(f"Drug not found: {drug_id}")

        labels_result = await db.execute(
            select(DrugLabel, RegulatoryAuthority)
            .join(RegulatoryAuthority, DrugLabel.authority_id == RegulatoryAuthority.id)
            .where(DrugLabel.drug_id == drug_id)
            .order_by(RegulatoryAuthority.country_code)
        )
        countries_data = []
        for label, auth in labels_result.all():
            sections_result = await db.execute(
                select(LabelSection)
                .where(LabelSection.label_id == label.id)
                .order_by(LabelSection.section_order)
            )
            sections = {s.section_name: s.content for s in sections_result.scalars().all()}
            countries_data.append(
                {
                    "country_code": auth.country_code,
                    "country_name": auth.country_name,
                    "authority_name": auth.authority_name,
                    "sections": sections,
                }
            )

        return {
            "drug": {
                "id": drug.id,
                "generic_name": drug.generic_name,
                "brand_name": drug.brand_name,
                "manufacturer": drug.manufacturer,
                "active_ingredient": drug.active_ingredient,
            },
            "countries": countries_data,
        }

    def _build_prompt(self, drug_data: Dict[str, Any]) -> str:
        drug = drug_data["drug"]
        countries = drug_data["countries"]

        prompt = (
            "You are a regulatory intelligence expert analyzing drug labels across countries.\n\n"
            "TASK: Generate a comprehensive cross-country regulatory comparison report.\n\n"
            "DRUG INFORMATION:\n"
            f"- Generic Name: {drug['generic_name']}\n"
            f"- Brand Name: {drug.get('brand_name') or 'N/A'}\n"
            f"- Manufacturer: {drug.get('manufacturer') or 'N/A'}\n"
            f"- Active Ingredient: {drug.get('active_ingredient') or 'N/A'}\n\n"
            "COUNTRIES COMPARED:\n"
        )

        key_sections = [
            "Indications and Usage",
            "Dosage and Administration",
            "Warnings and Precautions",
            "Adverse Reactions",
            "Contraindications",
            "Use in Specific Populations",
        ]

        for c in countries:
            prompt += f"\n{c['country_name']} ({c['country_code']}) - {c['authority_name']}"
            for sec in key_sections:
                if sec in c["sections"]:
                    content = c["sections"][sec]
                    if len(content) > 500:
                        content = content[:500] + "..."
                    prompt += f"\n\n  {sec}:\n  {content}"

        prompt += (
            "\n\nREQUIRED OUTPUT FORMAT (markdown):\n\n"
            "# Executive Summary\n"
            "Brief overview and 3-5 key findings.\n\n"
            "# Cross-Country Comparison\n"
            "For each key section: similarities, critical differences, regulatory implications.\n\n"
            "# Discrepancy Detection\n"
            "List discrepancies by severity (Critical / High / Medium / Low).\n\n"
            "# Country-Specific Notes\n"
            "Unique requirements per country.\n\n"
            "# Compliance Recommendations\n"
            "Actionable steps for alignment.\n\n"
            "# Appendix: Section Comparison\n"
            "Side-by-side table for each section.\n\n"
            "Be professional, specific, and actionable. Use markdown headings and tables."
        )
        return prompt

    async def generate_report(self, db: AsyncSession, drug_id: str) -> str:
        drug_data = await self.gather_drug_data(db, drug_id)
        prompt = self._build_prompt(drug_data)

        message = await asyncio.to_thread(
            self.client.messages.create,
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        report_text: str = message.content[0].text

        drug = drug_data["drug"]
        countries = drug_data["countries"]
        header = (
            "---\n"
            f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}  \n"
            f"**Drug:** {drug['generic_name']} ({drug.get('brand_name') or 'N/A'})  \n"
            f"**Countries Analyzed:** {', '.join(c['country_name'] for c in countries)}  \n"
            "**AI Model:** Anthropic Claude 3.5 Sonnet\n\n"
            "---\n\n"
        )
        return header + report_text


_instance: AIReportGenerator | None = None


def get_ai_generator() -> AIReportGenerator | None:
    global _instance
    if _instance is None:
        try:
            _instance = AIReportGenerator()
        except ValueError:
            return None
    return _instance
