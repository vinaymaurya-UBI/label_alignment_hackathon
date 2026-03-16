import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { 
  Search, 
  Sparkles, 
  ChevronRight, 
  Globe2, 
  Activity, 
  AlertCircle,
  Zap,
  LayoutGrid,
  Lightbulb,
  MousePointer2,
  FileText,
  Pill
} from "lucide-react";
import { useSemanticSearch } from "../hooks/useSemanticSearch";
import { cn } from "../lib/utils";

const COUNTRY_COLORS: Record<string, string> = {
  US: "bg-blue-600",
  EU: "bg-indigo-600",
  GB: "bg-cyan-600",
  CA: "bg-red-600",
  JP: "bg-amber-600",
  AU: "bg-emerald-600",
};

const EXAMPLE_QUERIES = [
  "drug interactions for HIV medications",
  "boxed warnings cardiovascular",
  "dosage adjustments in renal impairment",
  "pregnancy and lactation contraindications",
];

const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { data, isLoading, error, search } = useSemanticSearch();
  const [query, setQuery] = useState(searchParams.get("q") || "");

  useEffect(() => {
    const q = searchParams.get("q");
    if (q) {
      setQuery(q);
      search(q);
    }
  }, [searchParams, search]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) search(query.trim());
  };

  const handleExampleClick = (q: string) => {
    setQuery(q);
    search(q);
  };

  return (
    <div className="space-y-12 pb-20 text-left">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto text-left space-y-6 py-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-xs font-black text-primary uppercase tracking-widest border border-primary/20 animate-fade-in">
          <Sparkles className="w-4 h-4" />
          Neural Semantic Search
        </div>
        <h1 className="text-5xl font-black tracking-tight text-slate-900 leading-tight">
          Global Regulatory <span className="text-primary underline decoration-primary/20 underline-offset-8">Intelligence</span>
        </h1>
        <p className="text-xl text-slate-500 font-medium max-w-2xl text-left">
          Search across thousands of drug labels using natural language. Discover clinical insights, warnings, and protocols globally.
        </p>
      </div>

      {/* Search Input Box */}
      <div className="max-w-3xl mx-auto">
        <form 
          onSubmit={handleSubmit}
          className="group relative bg-white rounded-[2.5rem] p-2 shadow-2xl border border-slate-100 flex items-center gap-2 transition-all hover:border-primary/30 hover:ring-8 hover:ring-primary/5 focus-within:ring-8 focus-within:ring-primary/5 focus-within:border-primary/30"
        >
          <div className="flex-1 flex items-center px-4 gap-4">
            <Search className="w-6 h-6 text-slate-400 group-focus-within:text-primary transition-colors" />
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for clinical insights, warnings, or protocols..."
              className="w-full bg-transparent border-none py-4 text-lg font-bold text-slate-900 placeholder:text-slate-400 focus:ring-0 outline-none"
            />
          </div>
          <button 
            type="submit"
            disabled={isLoading}
            className={cn(
              "px-8 py-4 bg-slate-900 text-white rounded-[1.8rem] font-black transition-all flex items-center gap-2 shadow-lg",
              isLoading ? "bg-slate-700 animate-pulse" : "hover:bg-primary hover:-translate-y-0.5"
            )}
          >
            {isLoading ? (
              <Activity className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Zap className="w-5 h-5 fill-current" />
                Analyze
              </>
            )}
          </button>
        </form>

        {/* Suggested Queries */}
        {!data && !isLoading && (
          <div className="mt-10 animate-fade-in text-left px-4">
            <div className="flex items-center gap-3 mb-4">
              <Lightbulb className="w-4 h-4 text-amber-500" />
              <p className="text-xs font-black text-slate-400 uppercase tracking-widest">Suggested Queries</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => handleExampleClick(q)}
                  className="px-5 py-2.5 bg-white border border-slate-200 rounded-2xl text-sm font-bold text-slate-600 hover:border-primary hover:text-primary hover:bg-primary/5 transition-all flex items-center gap-2 group"
                >
                  <MousePointer2 className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Status Indicators */}
      {error && (
        <div className="max-w-3xl mx-auto bg-red-50 border border-red-100 p-6 rounded-3xl flex items-center gap-4 text-red-600">
          <AlertCircle className="w-6 h-6" />
          <p className="font-bold">{error}</p>
        </div>
      )}

      {data && data.length === 0 && (
        <div className="max-w-3xl mx-auto bg-slate-50 border border-slate-200 p-20 rounded-[3rem] text-center">
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
            <LayoutGrid className="w-10 h-10 text-slate-200" />
          </div>
          <h3 className="text-2xl font-black text-slate-900 tracking-tight">No Intelligence Found</h3>
          <p className="text-slate-500 font-medium mt-2">Try rephrasing your clinical query for broader jurisdictional results.</p>
        </div>
      )}

      {/* Results List */}
      {data && data.length > 0 && (
        <div className="max-w-4xl mx-auto space-y-8 animate-fade-in text-left">
          <div className="flex items-end justify-between px-6 border-b border-slate-100 pb-6">
            <div className="text-left">
              <h2 className="text-3xl font-black text-slate-900 tracking-tight">Clinical Insights</h2>
              <p className="text-slate-500 font-medium mt-1">Cross-jurisdictional matches for your query</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-400">Total Matches:</span>
              <span className="px-3 py-1 bg-slate-900 text-white rounded-lg text-xs font-black">{data.length}</span>
            </div>
          </div>

          <div className="space-y-6">
            {data.map((item) => (
              <div 
                key={item.section_id} 
                className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden group hover:shadow-xl hover:border-primary/20 transition-all duration-300 text-left"
              >
                <div className="px-8 py-6 border-b border-slate-50 bg-slate-50/20 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={cn(
                      "w-12 h-12 rounded-2xl flex items-center justify-center text-white font-black text-sm shadow-lg group-hover:scale-110 transition-transform",
                      COUNTRY_COLORS[item.country_code] || "bg-slate-400"
                    )}>
                      {item.country_code}
                    </div>
                    <div className="text-left">
                      <div className="flex items-center gap-2 mb-0.5">
                        <Pill className="w-3 h-3 text-primary" />
                        <h4 className="text-sm font-black text-primary uppercase tracking-wider">
                          {item.brand_name && item.brand_name !== 'N/A' ? item.brand_name : item.drug_name}
                        </h4>
                      </div>
                      <h4 className="text-lg font-black text-slate-800 leading-tight group-hover:text-slate-900 transition-colors">{item.heading}</h4>
                    </div>
                  </div>
                  <button 
                    onClick={() => navigate(`/drugs/${item.drug_id}`)}
                    className="p-3 bg-white rounded-xl border border-slate-100 text-slate-300 group-hover:text-primary group-hover:border-primary/20 transition-all shadow-sm"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
                
                <div className="p-8 text-left">
                  <div className="bg-slate-50/50 rounded-3xl p-8 border border-slate-100 relative overflow-hidden group/content">
                    <p className="text-slate-600 leading-relaxed font-medium line-clamp-6 text-lg italic relative z-10">
                      <FileText className="w-5 h-5 inline-block mr-3 text-slate-400 mb-1" />
                      "{item.content.slice(0, 1000)}{item.content.length > 1000 ? "..." : ""}"
                    </p>
                    <div className="mt-8 flex items-center justify-between relative z-10">
                      <button 
                        onClick={() => navigate(`/drugs/${item.drug_id}`)}
                        className="text-xs font-black text-primary hover:underline flex items-center gap-2 uppercase tracking-widest"
                      >
                        View full documentation
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                      <span className="text-[10px] font-black text-slate-300 uppercase tracking-[0.2em]">
                        Section Index: {item.section_id}
                      </span>
                    </div>
                    {/* Background decoration */}
                    <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover/content:opacity-[0.07] transition-opacity">
                      <FileText className="w-32 h-32" />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const ArrowRight = ({ className }: { className: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
);

export default SearchPage;
