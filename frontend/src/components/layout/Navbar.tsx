import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";
import { Link as RouterLink, useLocation } from "react-router-dom";

const links = [
  { label: "Drugs", to: "/" },
  { label: "Compare", to: "/compare" },
  { label: "Semantic Search", to: "/search" },
];

function Navbar() {
  const { pathname } = useLocation();

  return (
    <AppBar position="static" sx={{ background: "linear-gradient(135deg, #2563eb, #1d4ed8)" }}>
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
          Drug Label Alignment
        </Typography>
        <Box>
          {links.map((l) => (
            <Button
              key={l.to}
              color="inherit"
              component={RouterLink}
              to={l.to}
              sx={{ fontWeight: pathname === l.to ? 700 : 400, textDecoration: pathname === l.to ? "underline" : "none" }}
            >
              {l.label}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
