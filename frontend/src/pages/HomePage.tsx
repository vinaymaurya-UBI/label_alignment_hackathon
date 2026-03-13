import { Box, Typography, Grid, Paper, Stack } from "@mui/material";
import MedicationIcon from "@mui/icons-material/Medication";
import PublicIcon from "@mui/icons-material/Public";
import LibraryBooksIcon from "@mui/icons-material/LibraryBooks";
import LayersIcon from "@mui/icons-material/Layers";
import DrugGrid from "../components/drugs/DrugGrid";
import { useStats } from "../hooks/useDrugs";

function StatCard({ icon, value, label }: { icon: React.ReactNode; value: number | string; label: string }) {
  return (
    <Paper elevation={1} sx={{ p: 2, textAlign: "center" }}>
      <Stack spacing={0.5} alignItems="center">
        <Box sx={{ color: "primary.main" }}>{icon}</Box>
        <Typography variant="h5" fontWeight={700}>{value}</Typography>
        <Typography variant="caption" color="text.secondary">{label}</Typography>
      </Stack>
    </Paper>
  );
}

function HomePage() {
  const { data: stats } = useStats();

  return (
    <Stack spacing={4}>
      <Box
        sx={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          borderRadius: 2,
          p: 4,
          color: "#fff",
        }}
      >
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Global Drug Label Alignment Platform
        </Typography>
        <Typography variant="body1" mb={2}>
          AI-powered cross-country drug label comparison and regulatory intelligence.
        </Typography>
        {stats && (
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <StatCard icon={<MedicationIcon />} value={stats.drugs} label="Drugs" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatCard icon={<PublicIcon />} value={stats.countries} label="Countries" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatCard icon={<LibraryBooksIcon />} value={stats.labels} label="Labels" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatCard icon={<LayersIcon />} value={stats.sections} label="Sections" />
            </Grid>
          </Grid>
        )}
      </Box>

      <Box>
        <Typography variant="h5" fontWeight={700} gutterBottom>
          Drug Catalog
        </Typography>
        <DrugGrid />
      </Box>
    </Stack>
  );
}

export default HomePage;
