import React, { useState, useMemo, useEffect, useRef } from "react";
import { useParams, Link as RouterLink, useLocation } from "react-router-dom";
import { 
  ChevronRight, 
  ArrowLeftRight, 
  AlertTriangle, 
  CheckCircle2, 
  Globe2, 
  Activity,
  AlertCircle,
  FileText,
  Search,
  LayoutGrid,
  Zap,
  ChevronDown,
  Filter,
  Check
} from "lucide-react";
import { useDrugComparison } from "../hooks/useDrugComparison";
import { cn } from "../lib/utils";

const COUNTRY_COLORS: Record<string, string> = {
  US: "bg-blue-600",
  EU: "bg-indigo-600",
  GB: "bg-cyan-600",
  CA: "bg-red-600",
  JP: "bg-amber-600",
  AU: "bg-emerald-600",
};

const COUNTRY_NAMES: Record<string, string> = {
  US: "USA (FDA)",
  EU: "Europe (EMA)",
  GB: "UK (MHRA)",
  CA: "Canada (HC)",
  JP: "Japan (PMDA)",
  AU: "Australia (TGA)",
  IN: "India (CDSCO)"
};

const ComparisonSection = ({ section }: { section: any }) => {
  const hasDiscrepancy = section.entries.length > 1 &&
    new Set(section.entries.map((e: any) => e.content.trim().toLowerCase())).size > 1;

  return (
    <div className={cn(
      "bg-white rounded-[2rem] border shadow-sm overflow-hidden mb-10 transition-all duration-300 text-left",
      hasDiscrepancy ? "border-amber-200 ring-1 ring-amber-100/50 shadow-amber-50" : "border-slate-100"
    )}>
      <div className={cn(
        "px-8 py-5 flex items-center justify-between border-b sticky top-0 z-20 backdrop-blur-md",
        hasDiscrepancy ? "bg-amber-50/90 border-amber-100" : "bg-slate-50/90 border-slate-100"
      )}>
        <div className="flex items-center gap-4">
          <div className={cn(
            "p-2.5 rounded-xl shadow-sm",
            hasDiscrepancy ? "bg-white text-amber-600 border border-amber-100" : "bg-white text-emerald-600 border border-slate-100"
          )}>
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="text-xl font-black text-slate-900 tracking-tight">{section.section_heading}</h3>
        </div>

        <div className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest shadow-sm",
          hasDiscrepancy ? "bg-amber-600 text-white" : "bg-emerald-600 text-white"
        )}>
          {hasDiscrepancy ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5" />
              Discrepancy Detected
            </>
          ) : (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" />
              Aligned
            </>
          )}
        </div>
      </div>

      <div className="overflow-x-auto">
        <div className="min-w-full inline-block align-middle">
          <table className="min-w-full table-fixed divide-y divide-slate-100 text-left">
            <thead>
              <tr className="bg-slate-50/50">
                <th className="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest w-56">Jurisdiction</th>
                <th className="px-8 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Regulatory Intelligence & Technical Content</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {section.entries.map((entry: any) => (
                <tr key={entry.country_code} className="group hover:bg-slate-50/30 transition-all">
                  <td className="px-8 py-8 align-top">
                    <div className="flex flex-col items-center sticky top-24">
                      <div className={cn(
                        "w-14 h-14 rounded-2xl flex items-center justify-center text-white font-black text-xl shadow-lg group-hover:scale-110 transition-transform mb-3",
                        COUNTRY_COLORS[entry.country_code] || "bg-slate-400"
                      )}>
                        {entry.country_code}
                      </div>
                      <p className="text-[11px] font-black text-slate-900 text-center uppercase tracking-wider">
                        {COUNTRY_NAMES[entry.country_code] || entry.country_name}
                      </p>
                      <span className="mt-2 px-2 py-0.5 bg-slate-100 text-[9px] font-black text-slate-400 rounded-md uppercase">
                        Official Label
                      </span>
                    </div>
                  </td>
                  <td className="px-8 py-8 text-left">
                    <div className={cn(
                      "prose prose-slate max-w-none transition-colors",
                      hasDiscrepancy ? "text-slate-800" : "text-slate-600"
                    )}>
                      <div className="text-base leading-relaxed font-medium space-y-4 text-left">
                        {entry.content.split('\n').map((line: string, i: number) => (
                          line.trim() && <p key={i} className="mb-4 last:mb-0 text-left">{line}</p>
                        ))}
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const ComparePage = () => {
  const { drugId } = useParams<{ drugId: string }>();
  const location = useLocation();
  const { data, isLoading, error } = useDrugComparison(drugId);
  
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [appliedSections, setAppliedSections] = useState<string[]>([]);
  const [tempSections, setTempSections] = useState<string[]>([]);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Memoized query parameter parsing
  const regionFilter = useMemo(() => {
    const searchParams = new URLSearchParams(location.search);
    return searchParams.get("regions")?.split(",").filter(Boolean) || [];
  }, [location.search]);

  // Initial sections from URL or all data
  useEffect(() => {
    if (data?.comparisons) {
      const searchParams = new URLSearchParams(location.search);
      const urlSections = searchParams.get("sections")?.split(",").filter(Boolean) || [];
      
      const allHeadings = data.comparisons.map(c => c.section_heading);
      
      if (urlSections.length > 0) {
        // Find actual headings that match the URL filters (fuzzy)
        const normalize = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, '');
        const matched = allHeadings.filter(h => 
          urlSections.some(s => normalize(h).includes(normalize(s)) || normalize(s).includes(normalize(h)))
        );
        setAppliedSections(matched);
        setTempSections(matched);
      } else {
        setAppliedSections(allHeadings);
        setTempSections(allHeadings);
      }
    }
  }, [data, location.search]);

  // Handle clicks outside dropdown to close it
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsFilterOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const allHeadings = useMemo(() => 
    data?.comparisons?.map(c => c.section_heading) || [], 
    [data]
  );

  const toggleTempSection = (heading: string) => {
    setTempSections(prev => 
      prev.includes(heading) ? prev.filter(h => h !== heading) : [...prev, heading]
    );
  };

  const handleApplyFilter = () => {
    setAppliedSections(tempSections);
    setIsFilterOpen(false);
  };

  const handleSelectAll = () => setTempSections(allHeadings);
  const handleClearAll = () => setTempSections([]);

  // FINAL FILTERED DATA
  const filteredComparisons = useMemo(() => {
    if (!data?.comparisons) return [];
    
    let results = data.comparisons.filter(c => appliedSections.includes(c.section_heading));

    if (regionFilter.length > 0) {
      results = results.map(c => ({
        ...c,
        entries: c.entries.filter(e => regionFilter.includes(e.country_code))
      })).filter(c => c.entries.length > 0);
    }

    return results;
  }, [data, appliedSections, regionFilter]);

  const activeCountries = useMemo(() => 
    Array.from(new Set(filteredComparisons.flatMap((c) => c.entries.map((e) => e.country_code)))),
    [filteredComparisons]
  );

  const discrepancyCount = useMemo(() => 
    filteredComparisons.filter((s: any) => 
      s.entries.length > 1 && new Set(s.entries.map((e: any) => e.content.trim().toLowerCase())).size > 1
    ).length,
    [filteredComparisons]
  );

  const alignmentScore = useMemo(() => 
    filteredComparisons.length > 0 
      ? Math.round(((filteredComparisons.length - discrepancyCount) / filteredComparisons.length) * 100)
      : 100,
    [filteredComparisons, discrepancyCount]
  );

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-40 gap-4">
        <Activity className="w-12 h-12 text-primary animate-spin" />
        <p className="text-slate-500 font-bold text-lg animate-pulse">Analyzing cross-country alignment...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-100 p-8 rounded-3xl flex items-center gap-4 text-red-600">
        <AlertCircle className="w-6 h-6" />
        <p className="font-bold">Failed to load comparison data for this drug.</p>
      </div>
    );
  }

  return (
    <div className="space-y-10 pb-20 text-left">
      {/* Breadcrumbs */}
      <nav className="flex items-center gap-2 text-sm font-bold text-slate-400 text-left">
        <RouterLink to="/" className="hover:text-primary transition-colors">Drugs</RouterLink>
        <ChevronRight className="w-4 h-4" />
        <RouterLink to={`/drugs/${drugId}`} className="hover:text-primary transition-colors">{data.drug_name}</RouterLink>
        <ChevronRight className="w-4 h-4" />
        <span className="text-slate-900">Label Alignment</span>
      </nav>

      {/* Hero Header */}
      <div className="bg-slate-900 rounded-[3rem] p-10 text-white relative overflow-hidden shadow-2xl text-left">
        <div className="relative z-10 text-left">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 text-left">
            <div className="space-y-4 text-left">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full text-[10px] font-black uppercase tracking-widest border border-white/10">
                <ArrowLeftRight className="w-3.5 h-3.5 text-blue-400" />
                Comparison Engine v2.0
              </div>
              <h1 className="text-4xl font-black tracking-tight leading-tight text-left">Global Alignment <span className="text-blue-400">Analysis</span></h1>
              <p className="text-lg text-slate-300 font-medium text-left">
                {data.drug_name} <span className="mx-2 text-slate-600">•</span> {data.generic_name}
              </p>
            </div>

            <div className="flex flex-col gap-3">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-center md:text-right">Comparing Regions:</p>
              <div className="flex flex-wrap gap-2 justify-end">
                {activeCountries.map((cc) => (
                  <div 
                    key={cc} 
                    className={cn(
                      "px-3 py-1 rounded-lg text-xs font-black border border-white/10 backdrop-blur-md",
                      COUNTRY_COLORS[cc] || "bg-slate-700"
                    )}
                  >
                    {cc}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/2"></div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600">
            <LayoutGrid className="w-6 h-6" />
          </div>
          <div className="text-left">
            <p className="text-[10px] font-black text-slate-400 uppercase">Analyzed Sections</p>
            <p className="text-2xl font-black text-slate-900">{filteredComparisons.length}</p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 bg-amber-50 rounded-2xl flex items-center justify-center text-amber-600">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div className="text-left">
            <p className="text-[10px] font-black text-slate-400 uppercase">Discrepancies</p>
            <p className="text-2xl font-black text-slate-900">{discrepancyCount}</p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 bg-emerald-50 rounded-2xl flex items-center justify-center text-emerald-600">
            <Zap className="w-6 h-6" />
          </div>
          <div className="text-left">
            <p className="text-[10px] font-black text-slate-400 uppercase">Alignment Score</p>
            <p className="text-2xl font-black text-slate-900">{alignmentScore}%</p>
          </div>
        </div>
      </div>

      {/* Comparison Sections */}
      <div className="space-y-2 text-left">
        <div className="flex items-center justify-between px-2 mb-6">
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Regional Content Comparison</h2>
          
          {/* Section Filter Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button 
              onClick={() => setIsFilterOpen(!isFilterOpen)}
              className={cn(
                "flex items-center gap-3 px-5 py-3 rounded-2xl text-sm font-bold transition-all border shadow-sm",
                appliedSections.length < allHeadings.length
                  ? "bg-primary text-white border-primary shadow-primary/20"
                  : "bg-white text-slate-700 border-slate-200 hover:border-slate-300"
              )}
            >
              <Filter className="w-4 h-4" />
              <span>
                {appliedSections.length === allHeadings.length 
                  ? "All Sections" 
                  : `Filtered: ${appliedSections.length} sections`}
              </span>
              <ChevronDown className={cn("w-4 h-4 transition-transform", isFilterOpen && "rotate-180")} />
            </button>

            {isFilterOpen && (
              <div className="absolute right-0 mt-3 w-80 bg-white border border-slate-100 rounded-3xl shadow-2xl z-50 p-2 animate-in fade-in zoom-in duration-200 origin-top-right">
                <div className="p-4 border-b border-slate-50 flex items-center justify-between">
                  <span className="text-xs font-black text-slate-400 uppercase tracking-widest">Select Scope</span>
                  <div className="flex gap-3">
                    <button onClick={handleSelectAll} className="text-[10px] font-bold text-primary hover:underline">All</button>
                    <button onClick={handleClearAll} className="text-[10px] font-bold text-slate-400 hover:text-slate-600">None</button>
                  </div>
                </div>
                
                <div className="max-h-64 overflow-y-auto p-2 space-y-1">
                  {allHeadings.map((heading) => (
                    <button
                      key={heading}
                      onClick={() => toggleTempSection(heading)}
                      className={cn(
                        "w-full flex items-center justify-between p-3 rounded-xl text-left text-sm font-bold transition-colors",
                        tempSections.includes(heading) 
                          ? "bg-slate-50 text-slate-900" 
                          : "bg-white text-slate-500 hover:bg-slate-50/50"
                      )}
                    >
                      <span className="truncate pr-4">{heading}</span>
                      {tempSections.includes(heading) && (
                        <div className="w-5 h-5 bg-primary rounded-lg flex items-center justify-center shadow-sm">
                          <Check className="w-3.5 h-3.5 text-white" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>

                <div className="p-2 pt-0 mt-2 border-t border-slate-50">
                  <button 
                    onClick={handleApplyFilter}
                    className="w-full bg-slate-900 text-white py-3 rounded-xl text-sm font-bold hover:bg-slate-800 transition-all flex items-center justify-center gap-2 mt-2 shadow-lg shadow-slate-900/10"
                  >
                    Apply Filter
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {filteredComparisons.length === 0 ? (
          <div className="bg-slate-50 border-2 border-dashed border-slate-200 p-20 rounded-[3rem] text-center">
            <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
              <FileText className="w-10 h-10 text-slate-200" />
            </div>
            <h4 className="text-xl font-black text-slate-900">No matching sections found</h4>
            <p className="text-slate-500 font-medium mt-2">Try adjusting your section filters.</p>
            <button 
              onClick={() => {
                setTempSections(allHeadings);
                setAppliedSections(allHeadings);
              }}
              className="mt-6 text-sm font-bold text-primary hover:underline"
            >
              Reset to all sections
            </button>
          </div>
        ) : (
          filteredComparisons.map((section: any) => (
            <ComparisonSection key={section.section_heading} section={section} />
          ))
        )}
      </div>
    </div>
  );
};

export default ComparePage;
