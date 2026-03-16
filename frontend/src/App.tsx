import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import Sidebar from "./components/layout/Sidebar";
import HomePage from "./pages/HomePage";
import DrugDetailPage from "./pages/DrugDetailPage";
import ComparePage from "./pages/ComparePage";
import ReportPage from "./pages/ReportPage";
import SearchPage from "./pages/SearchPage";
import CompareWizardPage from "./pages/CompareWizardPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import HistoryPage from "./pages/HistoryPage";
import ActivityLogPage from "./pages/ActivityLogPage";
import { Search, Bell, User, Command } from "lucide-react";
import { useState, useEffect } from "react";

function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Redirect to home page with search query parameter
      navigate(`/?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery("");
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      
      <main className="flex-1 ml-72 flex flex-col min-h-screen">
        {/* Top Header */}
        <header className="h-20 bg-white/70 backdrop-blur-xl border-b border-slate-200/60 flex items-center justify-between px-10 sticky top-0 z-40 transition-all">
          <form onSubmit={handleSearch} className="relative w-[450px] group">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-2 pointer-events-none">
              <Search className="w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
            </div>
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search drugs, intelligence, or jurisdictions..." 
              className="w-full bg-slate-100/80 border border-transparent rounded-2xl py-2.5 pl-11 pr-12 text-sm font-medium focus:bg-white focus:border-primary/20 focus:ring-4 focus:ring-primary/5 transition-all outline-none"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 bg-white border border-slate-200 px-1.5 py-0.5 rounded-lg pointer-events-none opacity-50 group-focus-within:opacity-100 transition-opacity">
              <Command className="w-3 h-3 text-slate-500" />
              <span className="text-[10px] font-bold text-slate-500">K</span>
            </div>
          </form>

          <div className="flex items-center gap-6">
            <button className="flex items-center gap-3 pl-2 pr-1.5 py-1.5 rounded-2xl hover:bg-slate-100 transition-all border border-transparent hover:border-slate-200/60">
              <div className="w-10 h-10 bg-gradient-to-tr from-primary to-blue-400 rounded-xl flex items-center justify-center border border-white shadow-md shadow-primary/10">
                <User className="text-white w-5 h-5" />
              </div>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-10 animate-fade-in flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/drugs/:drugId" element={<DrugDetailPage />} />
            <Route path="/compare/selection" element={<CompareWizardPage />} />
            <Route path="/compare/:drugId" element={<ComparePage />} />
            <Route path="/reports/:drugId" element={<ReportPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/activity-log" element={<ActivityLogPage />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;
