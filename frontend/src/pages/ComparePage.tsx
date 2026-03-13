import { useParams, Link as RouterLink } from "react-router-dom";
import {
  Typography, Stack, Box, CircularProgress, Alert, Paper,
  Table, TableHead, TableRow, TableCell, TableBody, Chip, Breadcrumbs, Link,
} from "@mui/material";
import { useDrugComparison } from "../hooks/useDrugComparison";
import type { ComparisonEntry } from "../types";

const COUNTRY_COLORS: Record<string, string> = {
  US: "#2563eb", EU: "#7c3aed", GB: "#0891b2",
  CA: "#dc2626", JP: "#d97706", AU: "#16a34a", IN: "#ea580c",
};

function ComparePage() {
  const { drugId } = useParams<{ drugId: string }>();
  const { data, isLoading, error } = useDrugComparison(drugId);

  if (isLoading) return <Box textAlign="center" py={6}><CircularProgress /></Box>;
  if (error || !data) return <Alert severity="error">Failed to load comparison data.</Alert>;

  const allCountries = Array.from(
    new Set(data.comparisons.flatMap((c) => c.entries.map((e) => e.country_code)))
  );

  return (
    <Stack spacing={3}>
      <Breadcrumbs>
        <Link component={RouterLink} to="/">Drugs</Link>
        <Typography color="text.primary">{data.drug_name}</Typography>
        <Typography color="text.primary">Compare</Typography>
      </Breadcrumbs>

      <Box
        sx={{ background: "linear-gradient(135deg, #7c3aed, #4f46e5)", borderRadius: 2, p: 3, color: "#fff" }}
      >
        <Typography variant="h5" fontWeight={700}>{data.drug_name}</Typography>
        {data.generic_name && data.brand_name && (
          <Typography variant="body2">{data.generic_name}</Typography>
        )}
        {data.manufacturer && (
          <Typography variant="body2">Manufacturer: {data.manufacturer}</Typography>
        )}
        <Stack direction="row" spacing={1} mt={1}>
          {allCountries.map((cc) => (
            <Chip key={cc} label={cc} size="small" sx={{ bgcolor: COUNTRY_COLORS[cc] || "#64748b", color: "#fff" }} />
          ))}
        </Stack>
      </Box>

      {data.comparisons.length === 0 && (
        <Alert severity="info">No multi-country section data available for this drug yet.</Alert>
      )}

      {data.comparisons.map((section) => {
        const hasDiscrepancy = section.entries.length > 1 &&
          new Set(section.entries.map((e) => e.content)).size > 1;

        return (
          <Paper key={section.section_heading} elevation={1} sx={{ overflow: "hidden" }}>
            <Box
              sx={{
                p: 1.5, pl: 2,
                bgcolor: hasDiscrepancy ? "warning.light" : "primary.main",
                color: hasDiscrepancy ? "warning.contrastText" : "#fff",
                display: "flex", alignItems: "center", gap: 1,
              }}
            >
              <Typography variant="subtitle1" fontWeight={700}>{section.section_heading}</Typography>
              <Chip
                label={hasDiscrepancy ? "Discrepancy Found" : "Consistent"}
                size="small"
                color={hasDiscrepancy ? "warning" : "success"}
                sx={{ ml: "auto" }}
              />
            </Box>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ width: 100, fontWeight: 700 }}>Country</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Content</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {section.entries.map((entry: ComparisonEntry) => (
                  <TableRow key={entry.section_id} hover>
                    <TableCell>
                      <Chip
                        label={entry.country_code}
                        size="small"
                        sx={{ bgcolor: COUNTRY_COLORS[entry.country_code] || "#64748b", color: "#fff" }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ whiteSpace: "pre-wrap", fontSize: "0.8rem" }}>
                        {entry.content.slice(0, 600)}{entry.content.length > 600 ? "…" : ""}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        );
      })}
    </Stack>
  );
}

export default ComparePage;
