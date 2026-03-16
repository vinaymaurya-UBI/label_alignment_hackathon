import { Grid, TextField, MenuItem, Select, InputLabel, FormControl, InputAdornment, Box } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
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
    <Box
      sx={{
        p: 2,
        backgroundColor: "background.paper",
        borderRadius: 4,
        border: "1px solid",
        borderColor: "divider",
        mb: 3,
      }}
    >
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={5}>
          <TextField
            fullWidth
            placeholder="Search drugs by name or ingredient..."
            value={search}
            onChange={(e) => onSearch(e.target.value)}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: "text.disabled" }} />
                </InputAdornment>
              ),
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                backgroundColor: "#f8fafc",
              },
            }}
          />
        </Grid>
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Manufacturer</InputLabel>
            <Select
              value={manufacturer}
              label="Manufacturer"
              onChange={(e) => onManufacturer(e.target.value)}
              sx={{ backgroundColor: "#f8fafc" }}
            >
              <MenuItem value="">All Manufacturers</MenuItem>
              {manufacturers.map((m) => (
                <MenuItem key={m} value={m}>
                  {m}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={4}>
          <FormControl fullWidth size="small">
            <InputLabel>Country</InputLabel>
            <Select
              value={country}
              label="Country"
              onChange={(e) => onCountry(e.target.value)}
              sx={{ backgroundColor: "#f8fafc" }}
            >
              {COUNTRIES.map((c) => (
                <MenuItem key={c.code} value={c.code}>
                  {c.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DrugFilters;
