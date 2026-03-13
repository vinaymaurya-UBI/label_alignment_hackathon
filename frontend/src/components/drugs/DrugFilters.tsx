import { Grid, TextField, MenuItem, Select, InputLabel, FormControl } from "@mui/material";
import { useManufacturers } from "../../hooks/useDrugs";

const COUNTRIES = [
  { code: "", label: "All Countries" },
  { code: "US", label: "US (FDA)" },
  { code: "EU", label: "EU (EMA)" },
  { code: "GB", label: "UK (MHRA)" },
  { code: "CA", label: "Canada (Health Canada)" },
  { code: "JP", label: "Japan (PMDA)" },
  { code: "AU", label: "Australia (TGA)" },
];

interface Props {
  search: string;
  manufacturer: string;
  country: string;
  onSearch: (v: string) => void;
  onManufacturer: (v: string) => void;
  onCountry: (v: string) => void;
}

function DrugFilters({ search, manufacturer, country, onSearch, onManufacturer, onCountry }: Props) {
  const { data: manufacturers = [] } = useManufacturers();

  return (
    <Grid container spacing={2} alignItems="center">
      <Grid item xs={12} sm={5}>
        <TextField
          fullWidth
          label="Search drugs..."
          value={search}
          onChange={(e) => onSearch(e.target.value)}
          size="small"
        />
      </Grid>
      <Grid item xs={12} sm={3}>
        <FormControl fullWidth size="small">
          <InputLabel>Manufacturer</InputLabel>
          <Select value={manufacturer} label="Manufacturer" onChange={(e) => onManufacturer(e.target.value)}>
            <MenuItem value="">All Manufacturers</MenuItem>
            {manufacturers.map((m) => (
              <MenuItem key={m} value={m}>{m}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12} sm={4}>
        <FormControl fullWidth size="small">
          <InputLabel>Country</InputLabel>
          <Select value={country} label="Country" onChange={(e) => onCountry(e.target.value)}>
            {COUNTRIES.map((c) => (
              <MenuItem key={c.code} value={c.code}>{c.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  );
}

export default DrugFilters;
