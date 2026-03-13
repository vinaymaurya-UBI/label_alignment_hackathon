import { CssBaseline, Container } from "@mui/material";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/layout/Navbar";
import HomePage from "./pages/HomePage";
import DrugDetailPage from "./pages/DrugDetailPage";
import ComparePage from "./pages/ComparePage";
import ReportPage from "./pages/ReportPage";
import SearchPage from "./pages/SearchPage";

function App() {
  return (
    <>
      <CssBaseline />
      <Navbar />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 6 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/drugs/:drugId" element={<DrugDetailPage />} />
          <Route path="/compare/:drugId" element={<ComparePage />} />
          <Route path="/reports/:drugId" element={<ReportPage />} />
          <Route path="/search" element={<SearchPage />} />
        </Routes>
      </Container>
    </>
  );
}

export default App;
