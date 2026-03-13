-- Drug Label Alignment Platform - Database Initialization Script
-- This script creates all necessary tables, indexes, and initial data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Drugs catalog
CREATE TABLE drugs (
    drug_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generic_name VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255),
    manufacturer VARCHAR(255) NOT NULL,
    active_ingredient VARCHAR(255) NOT NULL,
    therapeutic_area VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Regulatory authorities
CREATE TABLE regulatory_authorities (
    authority_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_code VARCHAR(2) UNIQUE NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    authority_name VARCHAR(255) NOT NULL,
    api_endpoint VARCHAR(500),
    data_source_type VARCHAR(50) NOT NULL CHECK (data_source_type IN ('API', 'SCRAPER', 'DOCUMENT')),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'
);

-- Drug labels with versioning
CREATE TABLE drug_labels (
    label_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drug_id UUID NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    authority_id UUID NOT NULL REFERENCES regulatory_authorities(authority_id),
    version INTEGER NOT NULL,
    label_type VARCHAR(50) NOT NULL CHECK (label_type IN ('PACKAGE_INSERT', 'SMPC', 'PATIENT_LEAFLET')),
    effective_date DATE NOT NULL,
    raw_content TEXT,
    pdf_path VARCHAR(500),
    hash_sha256 CHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_drug_authority_version UNIQUE (drug_id, authority_id, version)
);

-- Structured label sections
CREATE TABLE label_sections (
    section_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label_id UUID NOT NULL REFERENCES drug_labels(label_id) ON DELETE CASCADE,
    section_name VARCHAR(100) NOT NULL,
    section_order INTEGER NOT NULL,
    content TEXT NOT NULL,
    normalized_content TEXT,
    entities JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Label comparisons
CREATE TABLE label_comparisons (
    comparison_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drug_id UUID NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    comparison_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comparison_config JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comparison results / discrepancies
CREATE TABLE comparison_discrepancies (
    discrepancy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comparison_id UUID NOT NULL REFERENCES label_comparisons(comparison_id) ON DELETE CASCADE,
    section_name VARCHAR(100) NOT NULL,
    discrepancy_type VARCHAR(50) NOT NULL CHECK (discrepancy_type IN ('ADDITION', 'DELETION', 'MODIFICATION', 'SEMANTIC_DIFF')),
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    description TEXT NOT NULL,
    country_1_id UUID REFERENCES regulatory_authorities(authority_id),
    country_2_id UUID REFERENCES regulatory_authorities(authority_id),
    content_1 TEXT,
    content_2 TEXT,
    similarity_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Change detection log
CREATE TABLE regulatory_changes (
    change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drug_id UUID NOT NULL REFERENCES drugs(drug_id) ON DELETE CASCADE,
    authority_id UUID NOT NULL REFERENCES regulatory_authorities(authority_id),
    previous_label_id UUID REFERENCES drug_labels(label_id),
    new_label_id UUID REFERENCES drug_labels(label_id),
    change_summary TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ingestion jobs tracking
CREATE TABLE ingestion_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    authority_id UUID NOT NULL REFERENCES regulatory_authorities(authority_id),
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('FULL_SYNC', 'INCREMENTAL', 'CHANGE_DETECTION')),
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_drugs_generic ON drugs(generic_name);
CREATE INDEX idx_drugs_manufacturer ON drugs(manufacturer);
CREATE INDEX idx_drugs_therapeutic_area ON drugs(therapeutic_area);

CREATE INDEX idx_labels_drug ON drug_labels(drug_id);
CREATE INDEX idx_labels_authority ON drug_labels(authority_id);
CREATE INDEX idx_labels_effective_date ON drug_labels(effective_date);
CREATE INDEX idx_labels_hash ON drug_labels(hash_sha256);
CREATE INDEX idx_labels_drug_authority ON drug_labels(drug_id, authority_id);

CREATE INDEX idx_sections_label ON label_sections(label_id);
CREATE INDEX idx_sections_name ON label_sections(section_name);
CREATE INDEX idx_sections_label_name ON label_sections(label_id, section_name);

CREATE INDEX idx_comparisons_drug ON label_comparisons(drug_id);
CREATE INDEX idx_comparisons_status ON label_comparisons(status);
CREATE INDEX idx_comparisons_date ON label_comparisons(comparison_date);

CREATE INDEX idx_discrepancies_comparison ON comparison_discrepancies(comparison_id);
CREATE INDEX idx_discrepancies_severity ON comparison_discrepancies(severity);
CREATE INDEX idx_discrepancies_section ON comparison_discrepancies(section_name);

CREATE INDEX idx_changes_drug ON regulatory_changes(drug_id);
CREATE INDEX idx_changes_authority ON regulatory_changes(authority_id);
CREATE INDEX idx_changes_detected_at ON regulatory_changes(detected_at);

CREATE INDEX idx_jobs_authority ON ingestion_jobs(authority_id);
CREATE INDEX idx_jobs_status ON ingestion_jobs(status);
CREATE INDEX idx_jobs_type ON ingestion_jobs(job_type);
CREATE INDEX idx_jobs_created_at ON ingestion_jobs(created_at);

-- Create triggers for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_drugs_updated_at BEFORE UPDATE ON drugs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Seed initial regulatory authorities
INSERT INTO regulatory_authorities (country_code, country_name, authority_name, api_endpoint, data_source_type, is_active, metadata) VALUES
('US', 'United States', 'U.S. Food and Drug Administration', 'https://api.fda.gov/drug/label.json', 'API', true, '{"rate_limit": 1000, "authentication": "API_KEY", "data_format": "JSON"}'::jsonb),
('JP', 'Japan', 'Pharmaceuticals and Medical Devices Agency', 'https://www.pmda.go.jp', 'SCRAPER', true, '{"rate_limit": 100, "authentication": "NONE", "data_format": "PDF", "languages": ["ja", "en"]}'::jsonb),
('IN', 'India', 'Central Drugs Standard Control Organization', 'https://cdsco.gov.in', 'SCRAPER', true, '{"rate_limit": 50, "authentication": "NONE", "data_format": "PDF"}'::jsonb)
ON CONFLICT (country_code) DO NOTHING;

-- Create function to generate hash for content comparison
CREATE OR REPLACE FUNCTION generate_content_hash(content TEXT)
RETURNS CHAR(64) AS $$
BEGIN
    IF content IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN encode(digest(content, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create view for active labels (latest version per drug/authority)
CREATE OR REPLACE VIEW active_labels AS
SELECT DISTINCT ON (dl.drug_id, dl.authority_id)
    dl.label_id,
    dl.drug_id,
    dl.authority_id,
    dl.version,
    dl.label_type,
    dl.effective_date,
    dl.pdf_path,
    dl.created_at,
    d.generic_name,
    d.brand_name,
    d.manufacturer,
    ra.country_code,
    ra.country_name,
    ra.authority_name
FROM drug_labels dl
JOIN drugs d ON dl.drug_id = d.drug_id
JOIN regulatory_authorities ra ON dl.authority_id = ra.authority_id
WHERE ra.is_active = true
ORDER BY dl.drug_id, dl.authority_id, dl.version DESC, dl.effective_date DESC;

-- Grant necessary permissions (adjust as needed for your environment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO drug_ra_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO drug_ra_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO drug_ra_user;

COMMIT;
