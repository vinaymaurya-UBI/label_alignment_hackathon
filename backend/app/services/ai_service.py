"""
AI report generation using Anthropic Claude or Google Gemini.
"""
import asyncio
from datetime import datetime
from typing import Any, Dict

import anthropic
import google.generativeai as genai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Drug, DrugLabel, LabelSection, RegulatoryAuthority


class AIReportGenerator:
    def __init__(self) -> None:
        # Anthropic setup
        ant_key = (settings.ANTHROPIC_API_KEY or "").strip()
        self.anthropic_client = None
        if ant_key:
            base_url = settings.ANTHROPIC_BASE_URL
            if base_url:
                self.anthropic_client = anthropic.Anthropic(api_key=ant_key, base_url=base_url)
            else:
                self.anthropic_client = anthropic.Anthropic(api_key=ant_key)

        # Gemini setup
        gem_key = (settings.GOOGLE_API_KEY or "").strip()
        self.gemini_enabled = False
        if gem_key:
            genai.configure(api_key=gem_key)
            self.gemini_enabled = True

        if not self.anthropic_client and not self.gemini_enabled:
            raise ValueError("No AI provider configured (missing ANTHROPIC_API_KEY or GOOGLE_API_KEY)")

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
            "You are a Senior Regulatory Intelligence Expert. Generate a clean, professional comparison report.\n\n"
            "DRUG:\n"
            f"- Generic: {drug['generic_name']}\n"
            f"- Brand: {drug.get('brand_name') or 'N/A'}\n\n"
            "DATA SOURCES:\n"
        )

        for c in countries:
            prompt += f"\n{c['country_name']} ({c['country_code']}):\n"
            for sec_name, content in c["sections"].items():
                snippet = (content[:500] + "...") if len(content) > 500 else content
                prompt += f"- {sec_name}: {snippet}\n"

        prompt += (
            "\nREQUIRED OUTPUT FORMAT (Markdown):\n\n"
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
            "# Appendix: Section Comparison Matrix\n"
            "Create ONE large, proper table comparing all sections across countries.\n"
            "Each row should be a Section, and each column should be a Country.\n"
            "Example:\n"
            "| Section | " + " | ".join([c['country_code'] for c in countries]) + " |\n"
            "| :--- | " + " | ".join([":---" for _ in countries]) + " |\n"
            "| Indications | [Content] | [Content] |\n"
            "| Dosage | [Content] | [Content] |\n\n"
            "STYLE RULES:\n"
            "- Be professional, specific, and actionable.\n"
            "- Use markdown headings and tables.\n"
            "- AVOID BOLDING (**text**) inside table cells.\n"
            "- Ensure every row starts and ends with a pipe (|).\n"
            "- Use clinical, neutral, and expert language."
        )
        return prompt

    async def generate_report(self, db: AsyncSession, drug_id: str) -> str:
        drug_data = await self.gather_drug_data(db, drug_id)
        prompt = self._build_prompt(drug_data)
        
        report_text = None
        provider_info = None

        # 1. Try Gemini (Primary - Verified gemini-2.5-flash)
        if self.gemini_enabled:
            try:
                model_name = settings.GOOGLE_MODEL
                model = genai.GenerativeModel(model_name)
                response = await asyncio.to_thread(model.generate_content, prompt)
                if response and response.text:
                    report_text = response.text
                    provider_info = f"Google Gemini ({model_name})"
            except Exception as e:
                print(f"Gemini failed: {e}")

        # 2. Try Anthropic (Fallback)
        if not report_text and self.anthropic_client:
            try:
                message = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=4096,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}],
                )
                report_text = message.content[0].text
                provider_info = f"Anthropic Claude ({settings.ANTHROPIC_MODEL})"
            except Exception as e:
                print(f"Anthropic failed: {e}")

        # 3. Final Resort: Fail
        if not report_text:
            raise RuntimeError("AI report generation failed.")

        drug = drug_data["drug"]
        countries = drug_data["countries"]
        
        header = (
            "---\n"
            f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}  \n"
            f"**Drug:** {drug['generic_name']} ({drug.get('brand_name') or 'N/A'})  \n"
            f"**Countries Analyzed:** {', '.join(c['country_name'] for c in countries)}  \n"
            f"**Intelligence Provider:** {provider_info}\n"
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
