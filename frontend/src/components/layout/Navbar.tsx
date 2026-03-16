import { AppBar, Toolbar, Typography, Button, Box, Container, alpha } from "@mui/material";
import { Link as RouterLink, useLocation } from "react-router-dom";
import MedicationIcon from "@mui/icons-material/Medication";

const links = [
  { label: "Drugs", to: "/" },
  { label: "Compare", to: "/compare" },
  { label: "Semantic Search", to: "/search" },
];

function Navbar() {
  const { pathname } = useLocation();

  return (
    <AppBar position="sticky">
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Box
            component={RouterLink}
            to="/"
            sx={{
              display: "flex",
              alignItems: "center",
              textDecoration: "none",
              color: "primary.main",
              mr: 4,
            }}
          >
            <MedicationIcon sx={{ mr: 1, fontSize: 28, color: "primary.main" }} />
            <Typography
              variant="h6"
              noWrap
              sx={{
                fontWeight: 800,
                letterSpacing: "-0.02em",
                color: "text.primary",
              }}
            >
              NeuroNext
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1, display: "flex", gap: 1 }}>
            {links.map((l) => {
              const isActive = pathname === l.to;
              return (
                <Button
                  key={l.to}
                  component={RouterLink}
                  to={l.to}
                  sx={{
                    color: isActive ? "primary.main" : "text.secondary",
                    backgroundColor: isActive ? (theme) => alpha(theme.palette.primary.main, 0.08) : "transparent",
                    "&:hover": {
                      color: "primary.main",
                      backgroundColor: (theme) => alpha(theme.palette.primary.main, 0.04),
                    },
                    px: 2,
                    borderRadius: 2,
                  }}
                >
                  {l.label}
                </Button>
              );
            })}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}

export default Navbar;
