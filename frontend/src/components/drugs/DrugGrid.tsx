import { useState, useCallback } from "react";
import { Grid, Pagination, Typography, Box, CircularProgress, Alert } from "@mui/material";
import { useDrugs, type DrugFilters } from "../../hooks/useDrugs";
import DrugCard from "./DrugCard";
import DrugFilters from "./DrugFilters";

const PAGE_SIZE = 12;

function DrugGrid() {
  const [filters, setFilters] = useState<DrugFilters>({
    search: "",
    manufacturer: "",
    country: "",
    limit: PAGE_SIZE,
    offset: 0,
  });
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useDrugs(filters);

  const update = useCallback((patch: Partial<DrugFilters>) => {
    setFilters((f) => ({ ...f, ...patch, offset: 0 }));
    setPage(1);
  }, []);

  const handlePage = (_: unknown, p: number) => {
    setPage(p);
    setFilters((f) => ({ ...f, offset: (p - 1) * PAGE_SIZE }));
  };

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;

  return (
    <Box>
      <DrugFilters
        search={filters.search ?? ""}
        manufacturer={filters.manufacturer ?? ""}
        country={filters.country ?? ""}
        onSearch={(v) => update({ search: v })}
        onManufacturer={(v) => update({ manufacturer: v })}
        onCountry={(v) => update({ country: v })}
      />

      <Box mt={2} mb={1} display="flex" alignItems="center" gap={1}>
        {isLoading && <CircularProgress size={18} />}
        {!isLoading && data && (
          <Typography variant="body2" color="text.secondary">
            Showing {data.drugs.length} of {data.total} drugs
          </Typography>
        )}
      </Box>

      {error && <Alert severity="error">Failed to load drugs. Is the backend running?</Alert>}

      <Grid container spacing={2}>
        {data?.drugs.map((drug) => (
          <Grid item xs={12} sm={6} md={4} key={drug.id}>
            <DrugCard drug={drug} />
          </Grid>
        ))}
      </Grid>

      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={3}>
          <Pagination count={totalPages} page={page} onChange={handlePage} color="primary" />
        </Box>
      )}
    </Box>
  );
}

export default DrugGrid;
