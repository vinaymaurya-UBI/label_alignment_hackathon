import { useState } from "react";
import {
  Stack, Typography, TextField, Button, Card, CardContent,
  Chip, Box, CircularProgress, Alert, InputAdornment,
} from "@mui/material";
import { useSemanticSearch } from "../hooks/useSemanticSearch";

const COUNTRY_COLORS: Record<string, string> = {
  US: "#2563eb", EU: "#7c3aed", GB: "#0891b2",
  CA: "#dc2626", JP: "#d97706", AU: "#16a34a", IN: "#ea580c",
};

const EXAMPLE_QUERIES = [
  "drug interactions for HIV medications",
  "boxed warnings cardiovascular",
  "dosage adjustments in renal impairment",
  "pregnancy and lactation contraindications",
];

function SearchPage() {
  const [query, setQuery] = useState("");
  const { data, isLoading, error, search } = useSemanticSearch();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) search(query.trim());
  };

  return (
    <Stack spacing={3}>
      <Typography variant="h4" fontWeight={700}>Semantic Search</Typography>
      <Typography variant="body1" color="text.secondary">
        Search across all drug label sections using natural language queries.
      </Typography>

      <Box component="form" onSubmit={handleSubmit}>
        <Stack direction="row" spacing={1}>
          <TextField
            fullWidth
            placeholder="e.g. drug interactions for HIV medications, boxed warnings..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <span style={{ fontSize: 18 }}>🔍</span>
                </InputAdornment>
              ),
            }}
          />
          <Button
            type="submit"
            variant="contained"
            disabled={isLoading}
            sx={{ minWidth: 110 }}
          >
            {isLoading ? <CircularProgress size={18} color="inherit" /> : "Search"}
          </Button>
        </Stack>
      </Box>

      {/* Example queries */}
      {!data && !isLoading && (
        <Box>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Try an example:
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {EXAMPLE_QUERIES.map((q) => (
              <Chip
                key={q}
                label={q}
                size="small"
                clickable
                variant="outlined"
                onClick={() => { setQuery(q); search(q); }}
              />
            ))}
          </Stack>
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {data && data.length === 0 && (
        <Alert severity="info">No results found. Try a different query.</Alert>
      )}

      {data && data.length > 0 && (
        <Stack spacing={2}>
          <Typography variant="body2" color="text.secondary">
            {data.length} result{data.length !== 1 ? "s" : ""} found
          </Typography>
          {data.map((item) => (
            <Card key={item.section_id} elevation={1}>
              <CardContent>
                <Stack direction="row" spacing={1} alignItems="center" mb={1} flexWrap="wrap">
                  <Chip
                    label={item.country_code}
                    size="small"
                    sx={{
                      bgcolor: COUNTRY_COLORS[item.country_code] || "#64748b",
                      color: "#fff",
                      fontWeight: 700,
                    }}
                  />
                  <Typography variant="subtitle2" fontWeight={700}>
                    {item.heading}
                  </Typography>
                </Stack>
                <Typography
                  variant="body2"
                  sx={{ whiteSpace: "pre-wrap", lineHeight: 1.7 }}
                >
                  {item.content.slice(0, 500)}{item.content.length > 500 ? "…" : ""}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}
    </Stack>
  );
}

export default SearchPage;
