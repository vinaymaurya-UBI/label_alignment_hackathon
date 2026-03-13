"""
ORM models that reflect the existing drug_ra.db schema.
"""
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Drug(Base):
    __tablename__ = "drugs"

    id = Column(String, primary_key=True, default=_uuid)
    generic_name = Column(String(255), nullable=False, index=True)
    brand_name = Column(String(255), index=True)
    manufacturer = Column(String(255))
    active_ingredient = Column(String(255))
    therapeutic_area = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    meta = Column(JSON, default={})

    labels = relationship("DrugLabel", back_populates="drug", cascade="all, delete-orphan")


class RegulatoryAuthority(Base):
    __tablename__ = "regulatory_authorities"

    id = Column(String, primary_key=True, default=_uuid)
    country_code = Column(String(2), unique=True, nullable=False)
    country_name = Column(String(100), nullable=False)
    authority_name = Column(String(255), nullable=False)
    api_endpoint = Column(String(500))
    data_source_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    meta = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())

    labels = relationship("DrugLabel", back_populates="authority")


class DrugLabel(Base):
    __tablename__ = "drug_labels"

    id = Column(String, primary_key=True, default=_uuid)
    drug_id = Column(String, ForeignKey("drugs.id"), nullable=False)
    authority_id = Column(String, ForeignKey("regulatory_authorities.id"), nullable=False)
    version = Column(Integer, nullable=False)
    label_type = Column(String(50), nullable=False)
    effective_date = Column(DateTime, nullable=False, index=True)
    raw_content = Column(Text)
    pdf_path = Column(String(500))
    hash_sha256 = Column(String(64))
    meta = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())

    drug = relationship("Drug", back_populates="labels")
    authority = relationship("RegulatoryAuthority", back_populates="labels")
    sections = relationship("LabelSection", back_populates="label", cascade="all, delete-orphan")


class LabelSection(Base):
    __tablename__ = "label_sections"

    id = Column(String, primary_key=True, default=_uuid)
    label_id = Column(String, ForeignKey("drug_labels.id"), nullable=False)
    section_name = Column(String(100), nullable=False, index=True)
    section_order = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    normalized_content = Column(Text)
    entities = Column(JSON, default={})
    embedding_id = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

    label = relationship("DrugLabel", back_populates="sections")
