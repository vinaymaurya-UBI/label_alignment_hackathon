import React, { useState } from "react";
import { useParams, Link as RouterLink } from "react-router-dom";
import { 
  ChevronRight, 
  ArrowLeftRight, 
  Zap, 
  Globe2, 
  Activity, 
  FileText,
  Clock,
  ExternalLink,
  Plus,
  Minus,
  AlertCircle,
  Building2,
  Stethoscope
} from "lucide-react";
import { useDrugDetail } from "../hooks/useDrugDetail";
import { cn } from "../lib/utils";
import GlobalMap from "../components/reports/GlobalMap";
import AiSummary from "../components/reports/AiSummary";

const COUNTRY_COLORS: Record<string, string> = {
  US: "bg-blue-600",
  EU: "bg-indigo-600",
  GB: "bg-cyan-600",
  CA: "bg-red-600",
  JP: "bg-amber-600",
  AU: "bg-emerald-600",
};

const COUNTRY_FULL_NAMES: Record<string, string> = {
  US: "United States (FDA)",
  EU: "European Union (EMA)",
  GB: "United Kingdom (MHRA)",
  CA: "Canada (Health Canada)",
  JP: "Japan (PMDA)",
  AU: "Australia (TGA)",
};

type SectionType = "uses" | "dosage" | "adverse" | "description" | "overdosage" | "ingredients" | "other";

const SECTION_TYPE_KEYWORDS: Array<[SectionType, string[]]> = [
  ["uses",        ["indication", "therapeutic", "indications and usage", "indications and clinical"]],
  ["dosage",      ["dosage", "posology", "method of administration"]],
  ["adverse",     ["adverse", "undesirable", "side effect"]],
  ["overdosage",  ["overdos", "overdose"]],
  ["ingredients", ["ingredient", "composition", "qualitative", "quantitative", "packaging"]],
  ["description", ["description", "pharmaceutical form", "properties", "pharmaceutical information"]],
];

const SECTION_COLORS: Record<SectionType, string> = {
  uses:        "bg-blue-500",
  dosage:      "bg-emerald-500",
  adverse:     "bg-rose-500",
  description: "bg-slate-500",
  overdosage:  "bg-purple-500",
  ingredients: "bg-amber-500",
  other:       "bg-slate-400",
};

function detectSectionType(sectionName: string): SectionType {
  const lower = sectionName.toLowerCase();
  for (const [type, keywords] of SECTION_TYPE_KEYWORDS) {
    if (keywords.some((kw) => lower.includes(kw))) return type;
  }
  return "other";
}

const SectionCard = ({ sectionName, content }: { sectionName: string; content: string }) => {
  const type = detectSectionType(sectionName);
  const colorClass = SECTION_COLORS[type];
  const isPlaceholder = content.startsWith("No data available");

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden mb-4 transition-all hover:shadow-md">
      <div className={cn("px-4 py-3 flex items-center justify-between border-b border-slate-50 bg-slate-50/20")}>
        <div className="flex items-center gap-3">
          <span className={cn("w-2 h-2 rounded-full", colorClass)}></span>
          <h4 className="text-sm font-black text-slate-800 uppercase tracking-tight">{sectionName}</h4>
        </div>
        <span className={cn("text-[9px] font-bold px-1.5 py-0.5 rounded uppercase text-white", colorClass)}>
          {type}
        </span>
      </div>
      <div className="p-5">
        <p className={cn(
          "text-sm leading-relaxed whitespace-pre-wrap",
          isPlaceholder ? "text-slate-400 italic" : "text-slate-600 font-medium"
        )}>
          {content}
        </p>
      </div>
    </div>
  );
};

const CountryLabelPanel = ({ label, isDefaultOpen }: { label: any; isDefaultOpen: boolean }) => {
  const [isOpen, setIsOpen] = useState(isDefaultOpen);
  const fullName = COUNTRY_FULL_NAMES[label.country_code] || label.country_code;

  return (
    <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden mb-6">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-5 flex items-center justify-between hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-5 text-left">
          <div className={cn(
            "w-12 h-12 rounded-2xl flex items-center justify-center text-white font-black text-lg shadow-lg shadow-primary/10",
            COUNTRY_COLORS[label.country_code] || "bg-slate-400"
          )}>
            {label.country_code}
          </div>
          <div>
            <h3 className="text-xl font-black text-slate-900 leading-none">{fullName}</h3>
            <p className="text-xs font-bold text-slate-400 mt-1.5 uppercase tracking-wider">
              {label.authority} • {label.label_type}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="px-3 py-1 bg-slate-100 rounded-full text-xs font-black text-slate-600">
            {label.sections.length} Sections
          </span>
          {isOpen ? <Minus className="w-5 h-5 text-slate-400" /> : <Plus className="w-5 h-5 text-slate-400" />}
        </div>
      </button>

      {isOpen && (
        <div className="px-6 pb-6 animate-fade-in">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8 bg-slate-50/50 p-4 rounded-2xl border border-slate-100">
            <div>
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Effective Date</p>
              <div className="flex items-center gap-2 text-sm font-bold text-slate-700">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                {label.effective_date ? new Date(label.effective_date).toLocaleDateString(undefined, { dateStyle: "long" }) : "N/A"}
              </div>
            </div>
            <div className="col-span-2">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Data Source</p>
              <div className="flex items-center gap-2 text-sm font-bold text-slate-700">
                <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                {label.data_source_name}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {label.sections
              .slice()
              .sort((a: any, b: any) => a.section_order - b.section_order)
              .map((section: any) => (
                <SectionCard 
                  key={section.id} 
                  sectionName={section.section_name} 
                  content={section.content} 
                />
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

const DrugDetailPage = () => {
  const { drugId } = useParams<{ drugId: string }>();
  const { data: drug, isLoading, error } = useDrugDetail(drugId ?? null);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-40 gap-4">
        <Activity className="w-12 h-12 text-primary animate-spin" />
        <p className="text-slate-500 font-bold text-lg animate-pulse">Loading drug data...</p>
      </div>
    );
  }

  if (error || !drug) {
    return (
      <div className="bg-red-50 border border-red-100 p-8 rounded-3xl flex items-center gap-4 text-red-600">
        <AlertCircle className="w-6 h-6" />
        <p className="font-bold">Drug not found or failed to load regulatory data.</p>
      </div>
    );
  }

  const name = drug.brand_name || drug.generic_name;

  return (
    <div className="space-y-10 pb-20">
      {/* Breadcrumbs */}
      <nav className="flex items-center gap-2 text-sm font-bold text-slate-400">
        <RouterLink to="/" className="hover:text-primary transition-colors">Drugs</RouterLink>
        <ChevronRight className="w-4 h-4" />
        <span className="text-slate-900">{name}</span>
      </nav>

      {/* Hero Header */}
      <div className="bg-slate-900 rounded-[3rem] p-10 text-white relative overflow-hidden shadow-2xl">
        <div className="relative z-10">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
            <div className="space-y-6 max-w-2xl">
              <div>
                <h1 className="text-5xl font-black tracking-tight mb-2 leading-tight">{name}</h1>
                {drug.brand_name && drug.generic_name && drug.brand_name !== drug.generic_name && (
                  <p className="text-xl text-slate-300 font-medium italic">
                    Generic: <span className="text-white font-bold">{drug.generic_name}</span>
                  </p>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-6 border-t border-white/10">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-white/10 rounded-2xl">
                    <Building2 className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Manufacturer</p>
                    <p className="text-lg font-bold">{drug.manufacturer || "N/A"}</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-white/10 rounded-2xl">
                    <Stethoscope className="w-5 h-5 text-indigo-400" />
                  </div>
                  <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Therapeutic Area</p>
                    <p className="text-lg font-bold">{drug.therapeutic_area || "N/A"}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-3 shrink-0">
              <RouterLink 
                to={`/compare/${drug.id}`}
                className="flex items-center justify-center gap-3 px-8 py-4 bg-primary text-white rounded-2xl font-black text-sm transition-all shadow-lg shadow-primary/20 hover:scale-105"
              >
                <ArrowLeftRight className="w-4 h-4" />
                Compare Global Labels
              </RouterLink>
              <RouterLink 
                to={`/reports/${drug.id}`}
                className="flex items-center justify-center gap-3 px-8 py-4 bg-white/10 text-white border border-white/10 rounded-2xl font-black text-sm transition-all backdrop-blur-sm hover:bg-white/20"
              >
                <Zap className="w-4 h-4 fill-current" />
                Generate AI Insights
              </RouterLink>
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-primary/20 rounded-full blur-[100px] pointer-events-none animate-pulse"></div>
      </div>

      {/* Main Grid: Map & AI Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="flex items-center justify-between px-2">
            <h3 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-3">
              <Globe2 className="w-6 h-6 text-primary" />
              Global Approval Map
            </h3>
          </div>
          <GlobalMap countries={drug.labels.map(l => l.country_code)} />
        </div>

        <div className="space-y-6">
          <div className="flex items-center justify-between px-2">
            <h3 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-3">
              <Zap className="w-6 h-6 text-amber-500" />
              Strategic Intelligence
            </h3>
          </div>
          <AiSummary drugId={drug.id} />
        </div>
      </div>

      {/* Regulatory Labels */}
      <div className="space-y-8 pt-6">
        <div className="flex items-end justify-between px-2 border-b border-slate-100 pb-6">
          <div>
            <h2 className="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-3">
              <FileText className="w-8 h-8 text-primary" />
              Regulatory Documents
            </h2>
            <p className="text-slate-500 font-medium mt-1">Official label data retrieved from global health authorities</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-400">Total Labels:</span>
            <span className="px-3 py-1 bg-slate-900 text-white rounded-lg text-xs font-black">{drug.labels.length}</span>
          </div>
        </div>

        <div className="max-w-4xl mx-auto">
          {drug.labels.length === 0 ? (
            <div className="bg-amber-50 border border-amber-100 p-10 rounded-[2.5rem] text-center">
              <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
              <h4 className="text-xl font-black text-amber-900">No label data available</h4>
              <p className="text-amber-700 font-medium mt-2">We couldn't find any official regulatory documents for this drug yet.</p>
            </div>
          ) : (
            drug.labels.map((label, idx) => (
              <CountryLabelPanel key={label.id} label={label} isDefaultOpen={idx === 0} />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default DrugDetailPage;
