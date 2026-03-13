import { Card, CardContent, CardActions, Typography, Button, Chip, Stack, Box } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import type { Drug } from "../../types";

interface Props {
  drug: Drug;
}

function DrugCard({ drug }: Props) {
  const name = drug.brand_name || drug.generic_name;
  const subtitle = drug.brand_name ? drug.generic_name : null;

  return (
    <Card
      component={RouterLink}
      to={`/drugs/${drug.id}`}
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        textDecoration: "none",
        color: "inherit",
        transition: "box-shadow 0.2s, transform 0.15s",
        "&:hover": { boxShadow: 8, transform: "translateY(-3px)" },
        cursor: "pointer",
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h6" fontWeight={700} gutterBottom noWrap title={name}>
          {name}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" gutterBottom noWrap>
            {subtitle}
          </Typography>
        )}
        {drug.manufacturer && (
          <Typography variant="caption" color="text.secondary" display="block" gutterBottom noWrap>
            {drug.manufacturer}
          </Typography>
        )}
        {drug.therapeutic_area && (
          <Chip label={drug.therapeutic_area} size="small" color="primary" variant="outlined" sx={{ mb: 1 }} />
        )}
        <Box mt={1}>
          <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
            {drug.country_codes.map((cc) => (
              <Chip key={cc} label={cc} size="small" sx={{ fontSize: "0.7rem" }} />
            ))}
          </Stack>
        </Box>
        <Typography variant="caption" color="text.secondary" mt={1} display="block">
          {drug.label_count} {drug.label_count === 1 ? "country" : "countries"}
        </Typography>
      </CardContent>

      <CardActions sx={{ pt: 0, gap: 0.5 }} onClick={(e) => e.stopPropagation()}>
        <Button size="small" component={RouterLink} to={`/drugs/${drug.id}`}>
          View Details
        </Button>
        <Button size="small" component={RouterLink} to={`/compare/${drug.id}`}>
          Compare
        </Button>
        <Button size="small" component={RouterLink} to={`/reports/${drug.id}`} color="secondary">
          AI Report
        </Button>
      </CardActions>
    </Card>
  );
}

export default DrugCard;
