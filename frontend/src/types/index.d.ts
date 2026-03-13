export interface Drug {
  id: string;
  generic_name: string;
  brand_name: string | null;
  manufacturer: string | null;
  active_ingredient: string | null;
  therapeutic_area: string | null;
  country_codes: string[];
  label_count: number;
}

export interface DrugListResponse {
  drugs: Drug[];
  total: number;
  limit: number;
  offset: number;
}

export interface LabelSection {
  id: string;
  section_name: string;
  section_order: number;
  content: string;
}

export interface DrugLabel {
  id: string;
  authority: string;
  country_code: string;
  label_type: string;
  effective_date: string | null;
  sections: LabelSection[];
  data_source_type: string;
  data_source_name: string;
  data_source_url: string;
}

export interface DrugDetail {
  id: string;
  generic_name: string;
  brand_name: string | null;
  manufacturer: string | null;
  active_ingredient: string | null;
  therapeutic_area: string | null;
  labels: DrugLabel[];
}

export interface ComparisonEntry {
  country_code: string;
  country_name: string;
  label_id: string;
  section_id: string;
  content: string;
}

export interface ComparisonSection {
  section_heading: string;
  entries: ComparisonEntry[];
}

export interface DrugComparison {
  drug_id: string;
  drug_name: string;
  generic_name: string;
  brand_name: string | null;
  manufacturer: string | null;
  comparisons: ComparisonSection[];
}

export interface PlatformStats {
  drugs: number;
  labels: number;
  sections: number;
  countries: number;
}

export interface SemanticSearchResult {
  section_id: string;
  label_id: string;
  drug_id: string;
  country_code: string;
  heading: string;
  content: string;
}
