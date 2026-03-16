import React from "react";
import { 
  Globe, 
  Search, 
  ArrowRight, 
  Sparkles, 
  ShieldCheck, 
  FileText, 
  TrendingUp,
  Activity,
  Zap
} from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { useStats } from "../hooks/useDrugs";
import DrugGrid from "../components/drugs/DrugGrid";
import { cn } from "../lib/utils";

const StatCard = ({ icon: Icon, value, label, color }: { 
  icon: any; 
  value: string | number; 
  label: string;
  color: string;
}) => (
  <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex items-center gap-5 transition-all duration-300 hover:shadow-glow group">
    <div className={cn(
      "p-3.5 rounded-2xl transition-all duration-300 group-hover:scale-110",
      color
    )}>
      <Icon className="w-6 h-6" />
    </div>
    <div>
      <h3 className="text-2xl font-bold text-slate-900 leading-tight">{value}</h3>
      <p className="text-sm font-medium text-slate-500 mt-0.5">{label}</p>
    </div>
  </div>
);

const HomePage = () => {
  const { data: stats } = useStats();
  const [searchParams] = useSearchParams();
  const searchQuery = searchParams.get("q") || undefined;

  return (
    <div className="space-y-10 text-left">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-slate-900 rounded-[2.5rem] p-12 text-white shadow-2xl">
        <div className="relative z-10 max-w-2xl text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 backdrop-blur-md rounded-full border border-white/10 text-xs font-semibold tracking-wider uppercase mb-6">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span>AI-Powered Regulatory Alignment</span>
          </div>
          <h1 className="text-5xl font-black tracking-tight mb-6 leading-[1.1]">
            Global Label <span className="text-blue-400">Intelligence</span> Dashboard
          </h1>
          <p className="text-lg text-slate-300 font-medium mb-10 leading-relaxed text-left">
            Real-time regulatory tracking, AI-driven discrepancy detection, and automated alignment verification across all major jurisdictions.
          </p>
          <div className="flex flex-wrap gap-4">
            <button 
              onClick={() => {
                const element = document.getElementById('catalog');
                element?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="bg-primary hover:bg-primary-dark text-white px-8 py-4 rounded-2xl font-bold transition-all flex items-center gap-2 shadow-lg shadow-primary/25"
            >
              Browse Portfolio
              <ArrowRight className="w-5 h-5" />
            </button>
            <button 
              onClick={() => window.location.href = '/search'}
              className="bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-2xl font-bold transition-all border border-white/10 backdrop-blur-sm"
            >
              Start Alignment Wizard
            </button>
          </div>
        </div>

        {/* Floating Globe Decorative */}
        <div className="absolute top-1/2 right-0 -translate-y-1/2 translate-x-1/4 w-[600px] h-[600px] opacity-20 pointer-events-none">
          <div className="w-full h-full bg-blue-500 rounded-full blur-[120px] absolute inset-0 animate-pulse"></div>
          <Globe className="w-full h-full text-white relative z-10" strokeWidth={0.5} />
        </div>
      </section>

      {/* Stats Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          icon={Activity} 
          value={stats?.drugs || 0} 
          label="Global Drugs" 
          color="bg-blue-50 text-blue-600"
        />
        <StatCard 
          icon={Globe} 
          value={stats?.countries || 0} 
          label="Jurisdictions" 
          color="bg-indigo-50 text-indigo-600" 
        />
        <StatCard 
          icon={ShieldCheck} 
          value={stats?.labels || 0} 
          label="Active Labels" 
          color="bg-emerald-50 text-emerald-600" 
        />
        <StatCard 
          icon={Zap} 
          value={stats?.sections || 0} 
          label="Data Points" 
          color="bg-amber-50 text-amber-600" 
        />
      </section>

      {/* Main Content Area */}
      <section id="catalog" className="space-y-6">
        <div className="flex items-end justify-between px-2">
          <div className="text-left">
            <h2 className="text-3xl font-black text-slate-900 tracking-tight">
              {searchQuery ? `Search Results for "${searchQuery}"` : "Drug Catalog"}
            </h2>
            <p className="text-slate-500 font-medium mt-1">Browse and analyze medical labels across global markets</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex bg-slate-100 p-1 rounded-xl">
              <button className="px-4 py-2 bg-white rounded-lg text-sm font-bold shadow-sm text-slate-900">All</button>
              <button className="px-4 py-2 rounded-lg text-sm font-bold text-slate-500 hover:text-slate-900">Approved</button>
              <button className="px-4 py-2 rounded-lg text-sm font-bold text-slate-500 hover:text-slate-900">Pending</button>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm min-h-[400px]">
          <DrugGrid search={searchQuery} />
        </div>
      </section>
    </div>
  );
};

export default HomePage;
