import { useParams, Link as RouterLink } from "react-router-dom";
import {
  Box, Typography, Stack, Chip, Breadcrumbs, Link, Button,
  CircularProgress, Alert, Divider, Paper, Card, CardContent,
  Grid, Collapse,
} from "@mui/material";
import { useState } from "react";
import { useDrugDetail } from "../hooks/useDrugDetail";

const COUNTRY_COLORS: Record<string, string> = {
  US: "#2563eb",
  EU: "#7c3aed",
  GB: "#0891b2",
  CA: "#dc2626",
  JP: "#d97706",
  AU: "#16a34a",
};

const COUNTRY_FULL_NAMES: Record<string, string> = {
  US: "United States (FDA)",
  EU: "European Union (EMA)",
  GB: "United Kingdom (MHRA)",
  CA: "Canada (Health Canada)",
  JP: "Japan (PMDA)",
  AU: "Australia (TGA)",
};

// Section type detection by keywords in section name
type SectionType = "uses" | "dosage" | "adverse" | "description" | "overdosage" | "ingredients" | "other";

const SECTION_TYPE_KEYWORDS: Array<[SectionType, string[]]> = [
  ["uses",        ["indication", "therapeutic", "indications and usage", "indications and clinical"]],
  ["dosage",      ["dosage", "posology", "method of administration"]],
  ["adverse",     ["adverse", "undesirable", "side effect"]],
  ["overdosage",  ["overdos", "overdose"]],
  ["ingredients", ["ingredient", "composition", "qualitative", "quantitative", "packaging"]],
  ["description", ["description", "pharmaceutical form", "properties", "pharmaceutical information"]],
];

const SECTION_COLORS: Record<SectionType, string> = {
  uses:        "#2563eb",
  dosage:      "#059669",
  adverse:     "#dc2626",
  description: "#475569",
  overdosage:  "#9333ea",
  ingredients: "#d97706",
  other:       "#64748b",
};

const SECTION_LABELS: Record<SectionType, string> = {
  uses:        "USES / INDICATIONS",
  dosage:      "DOSAGE & ADMINISTRATION",
  adverse:     "ADVERSE EFFECTS",
  description: "DESCRIPTION",
  overdosage:  "OVERDOSAGE",
  ingredients: "INGREDIENTS & COMPOSITION",
  other:       "INFORMATION",
};

function detectSectionType(sectionName: string): SectionType {
  const lower = sectionName.toLowerCase();
  for (const [type, keywords] of SECTION_TYPE_KEYWORDS) {
    if (keywords.some((kw) => lower.includes(kw))) return type;
  }
  return "other";
}

interface SectionCardProps {
  sectionName: string;
  content: string;
  countryColor: string;
}

function SectionCard({ sectionName, content }: SectionCardProps) {
  const type = detectSectionType(sectionName);
  const color = SECTION_COLORS[type];
  const label = SECTION_LABELS[type];

  const isPlaceholder = content.startsWith("No data available");

  return (
    <Card
      elevation={0}
      sx={{
        border: "1px solid",
        borderColor: "divider",
        borderLeft: `4px solid ${color}`,
        borderRadius: 1,
        mb: 1.5,
      }}
    >
      <CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
        {/* Section header */}
        <Box
          sx={{
            px: 2,
            py: 1,
            bgcolor: `${color}10`,
            borderBottom: "1px solid",
            borderColor: "divider",
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              bgcolor: color,
              flexShrink: 0,
            }}
          />
          <Typography variant="overline" fontWeight={700} color={color} lineHeight={1.5}>
            {label}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ ml: "auto", fontStyle: "italic" }}>
            {sectionName}
          </Typography>
        </Box>

        {/* Section content */}
        <Box sx={{ px: 2, py: 1.5 }}>
          {isPlaceholder ? (
            <Typography variant="body2" color="text.disabled" fontStyle="italic">
              {content}
            </Typography>
          ) : (
            <Typography
              variant="body2"
              sx={{
                whiteSpace: "pre-wrap",
                lineHeight: 1.9,
                color: "text.primary",
                fontSize: "0.855rem",
              }}
            >
              {content}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}

function CountryPanel({
  label,
  defaultOpen,
}: {
  label: { id: string; country_code: string; authority: string; data_source_type: string; label_type: string; effective_date?: string; data_source_name: string; sections: Array<{ id: string; section_name: string; content: string; section_order: number }> };
  defaultOpen: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const color = COUNTRY_COLORS[label.country_code] || "#64748b";
  const fullName = COUNTRY_FULL_NAMES[label.country_code] || label.country_code;

  return (
    <Paper elevation={2} sx={{ overflow: "hidden" }}>
      {/* Country header — click to expand/collapse */}
      <Box
        onClick={() => setOpen((v) => !v)}
        sx={{
          background: `linear-gradient(135deg, ${color} 0%, ${color}bb 100%)`,
          p: 2,
          display: "flex",
          alignItems: "center",
          gap: 1.5,
          cursor: "pointer",
          userSelect: "none",
          "&:hover": { opacity: 0.93 },
        }}
      >
        <Chip
          label={label.country_code}
          size="small"
          sx={{ bgcolor: "rgba(255,255,255,0.25)", color: "#fff", fontWeight: 700, fontSize: "0.8rem" }}
        />
        <Typography variant="h6" color="#fff" fontWeight={700} flexGrow={1}>
          {fullName}
        </Typography>
        <Chip
          label={`${label.sections.length} sections`}
          size="small"
          sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "#fff", fontSize: "0.7rem" }}
        />
        <Typography color="#fff" sx={{ opacity: 0.8, fontSize: 18 }}>
          {open ? "▲" : "▼"}
        </Typography>
      </Box>

      <Collapse in={open}>
        {/* Meta row */}
        <Box sx={{ px: 2, py: 1, bgcolor: "grey.50", borderBottom: "1px solid", borderColor: "divider" }}>
          <Stack direction="row" spacing={2} flexWrap="wrap">
            <Typography variant="caption" color="text.secondary">
              <strong>Type:</strong> {label.label_type}
            </Typography>
            {label.effective_date && (
              <Typography variant="caption" color="text.secondary">
                <strong>Effective:</strong> {new Date(label.effective_date).toLocaleDateString()}
              </Typography>
            )}
            <Typography variant="caption" color="text.secondary">
              <strong>Source:</strong> {label.data_source_name}
            </Typography>
          </Stack>
        </Box>

        {/* Sections */}
        <Box sx={{ p: 2 }}>
          {label.sections.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No sections available for this label.
            </Typography>
          ) : (
            label.sections
              .slice()
              .sort((a, b) => a.section_order - b.section_order)
              .map((section) => (
                <SectionCard
                  key={section.id}
                  sectionName={section.section_name}
                  content={section.content}
                  countryColor={color}
                />
              ))
          )}
        </Box>
      </Collapse>
    </Paper>
  );
}

function DrugDetailPage() {
  const { drugId } = useParams<{ drugId: string }>();
  const { data: drug, isLoading, error } = useDrugDetail(drugId ?? null);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !drug) {
    return <Alert severity="error">Drug not found or failed to load.</Alert>;
  }

  const name = drug.brand_name || drug.generic_name;

  return (
    <Stack spacing={3}>
      {/* Breadcrumb */}
      <Breadcrumbs>
        <Link component={RouterLink} to="/" underline="hover" color="inherit">
          Drugs
        </Link>
        <Typography color="text.primary">{name}</Typography>
      </Breadcrumbs>

      {/* Drug header */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)",
          borderRadius: 2,
          p: 3,
          color: "#fff",
        }}
      >
        <Typography variant="h4" fontWeight={700} gutterBottom>
          {name}
        </Typography>
        {drug.brand_name && drug.generic_name && drug.brand_name !== drug.generic_name && (
          <Typography variant="subtitle1" sx={{ opacity: 0.85 }} gutterBottom>
            Generic name: {drug.generic_name}
          </Typography>
        )}

        <Grid container spacing={2} mt={0.5}>
          {drug.manufacturer && (
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="caption" sx={{ opacity: 0.7, display: "block" }}>Manufacturer</Typography>
              <Typography variant="body2" fontWeight={600}>{drug.manufacturer}</Typography>
            </Grid>
          )}
          {drug.active_ingredient && (
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="caption" sx={{ opacity: 0.7, display: "block" }}>Active Ingredient</Typography>
              <Typography variant="body2" fontWeight={600}>{drug.active_ingredient}</Typography>
            </Grid>
          )}
          {drug.therapeutic_area && (
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="caption" sx={{ opacity: 0.7, display: "block" }}>Therapeutic Area</Typography>
              <Typography variant="body2" fontWeight={600}>{drug.therapeutic_area}</Typography>
            </Grid>
          )}
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" sx={{ opacity: 0.7, display: "block" }}>Approved Countries</Typography>
            <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap mt={0.5}>
              {drug.labels.map((l) => (
                <Chip
                  key={l.id}
                  label={l.country_code}
                  size="small"
                  sx={{ bgcolor: COUNTRY_COLORS[l.country_code] || "#475569", color: "#fff", fontWeight: 700 }}
                />
              ))}
            </Stack>
          </Grid>
        </Grid>

        {/* Action buttons */}
        <Stack direction="row" spacing={1} mt={2.5} flexWrap="wrap">
          <Button
            component={RouterLink}
            to={`/compare/${drug.id}`}
            variant="contained"
            sx={{ bgcolor: "rgba(255,255,255,0.2)", "&:hover": { bgcolor: "rgba(255,255,255,0.35)" } }}
          >
            Compare Countries
          </Button>
          <Button
            component={RouterLink}
            to={`/reports/${drug.id}`}
            variant="contained"
            sx={{ bgcolor: "rgba(255,255,255,0.2)", "&:hover": { bgcolor: "rgba(255,255,255,0.35)" } }}
          >
            Generate AI Report
          </Button>
        </Stack>
      </Box>

      {/* Section legend */}
      <Paper elevation={0} sx={{ p: 2, border: "1px solid", borderColor: "divider", bgcolor: "grey.50" }}>
        <Typography variant="caption" color="text.secondary" fontWeight={600} display="block" mb={1}>
          SECTION KEY
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {(Object.entries(SECTION_COLORS) as Array<[SectionType, string]>)
            .filter(([t]) => t !== "other")
            .map(([type, color]) => (
              <Chip
                key={type}
                label={SECTION_LABELS[type]}
                size="small"
                sx={{
                  bgcolor: `${color}15`,
                  color: color,
                  borderLeft: `3px solid ${color}`,
                  borderRadius: "4px",
                  fontWeight: 600,
                  fontSize: "0.68rem",
                }}
              />
            ))}
        </Stack>
      </Paper>

      {/* No labels */}
      {drug.labels.length === 0 && (
        <Alert severity="warning">
          No regulatory label data available for this drug yet.
        </Alert>
      )}

      {/* Per-country panels */}
      {drug.labels.map((label, idx) => (
        <CountryPanel key={label.id} label={label} defaultOpen={idx === 0} />
      ))}
    </Stack>
  );
}

export default DrugDetailPage;
