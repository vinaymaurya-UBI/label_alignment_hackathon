import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Search, 
  Globe2, 
  FileText, 
  ArrowRight, 
  CheckCircle2, 
  ChevronRight,
  Activity,
  AlertCircle,
  Building2,
  Zap,
  LayoutGrid
} from "lucide-react";
import { useDrugs } from "../hooks/useDrugs";
import { cn } from "../lib/utils";

const COUNTRY_NAMES: Record<string, string> = {
  US: "United States (FDA)",
  EU: "European Union (EMA)",
  GB: "United Kingdom (MHRA)",
  CA: "Canada (Health Canada)",
  JP: "Japan (PMDA)",
  AU: "Australia (TGA)",
  IN: "India (CDSCO)"
};

const COMPARE_SECTIONS = [
  "Indications & Usage",
  "Dosage & Administration",
  "Contraindications",
  "Warnings & Precautions",
  "Adverse Reactions",
  "Drug Interactions",
  "Use in Specific Populations",
  "Overdosage",
  "Clinical Pharmacology"
];

const CompareWizardPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDrug, setSelectedDrug] = useState<any>(null);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [selectedSections, setSelectedSections] = useState<string[]>(COMPARE_SECTIONS);

  const { data: drugResults, isLoading: drugsLoading } = useDrugs({ search: searchQuery });

  const handleDrugSelect = (drug: any) => {
    setSelectedDrug(drug);
    setSelectedCountries(drug.country_codes || []);
    setStep(2);
  };

  const toggleCountry = (code: string) => {
    setSelectedCountries(prev => 
      prev.includes(code) ? prev.filter(c => c !== code) : [...prev, code]
    );
  };

  const toggleSection = (section: string) => {
    setSelectedSections(prev => 
      prev.includes(section) ? prev.filter(s => s !== section) : [...prev, section]
    );
  };

  const handleCompare = () => {
    if (selectedDrug) {
      const regionsParam = selectedCountries.join(",");
      const sectionsParam = selectedSections.join(",");
      navigate(`/compare/${selectedDrug.id}?regions=${encodeURIComponent(regionsParam)}&sections=${encodeURIComponent(sectionsParam)}`);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-10 pb-20">
      {/* Header & Stepper */}
      <div className="space-y-6">
        <div className="flex items-center gap-3 px-2">
          <div className="w-12 h-12 bg-primary/10 rounded-2xl flex items-center justify-center text-primary">
            <Zap className="w-6 h-6 fill-current" />
          </div>
          <div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight">Alignment Wizard</h1>
            <p className="text-slate-500 font-medium">Configure your cross-jurisdictional comparison</p>
          </div>
        </div>

        <div className="flex items-center gap-4 bg-white p-4 rounded-3xl border border-slate-100 shadow-sm">
          {[1, 2, 3].map((s) => (
            <React.Fragment key={s}>
              <div className="flex items-center gap-3 flex-1">
                <div className={cn(
                  "w-10 h-10 rounded-xl flex items-center justify-center font-black text-sm transition-all",
                  step === s ? "bg-primary text-white shadow-lg shadow-primary/20" : 
                  step > s ? "bg-emerald-500 text-white" : "bg-slate-100 text-slate-400"
                )}>
                  {step > s ? <CheckCircle2 className="w-5 h-5" /> : s}
                </div>
                <span className={cn(
                  "text-sm font-bold transition-colors",
                  step === s ? "text-slate-900" : "text-slate-400"
                )}>
                  {s === 1 ? "Select Drug" : s === 2 ? "Choose Regions" : "Alignment"}
                </span>
              </div>
              {s < 3 && <ChevronRight className="w-5 h-5 text-slate-200" />}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Step 1: Drug Selection */}
      {step === 1 && (
        <div className="space-y-6 animate-fade-in">
          <div className="relative group">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-primary transition-colors" />
            <input 
              type="text" 
              placeholder="Search for a drug product (e.g., Remdesivir, Paxlovid)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-[2rem] py-5 pl-14 pr-6 text-lg font-bold text-slate-900 placeholder:text-slate-300 focus:ring-8 focus:ring-primary/5 focus:border-primary/30 transition-all outline-none shadow-sm"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {drugsLoading ? (
              <div className="col-span-2 py-20 flex flex-col items-center justify-center gap-4">
                <Activity className="w-10 h-10 text-primary animate-spin" />
                <p className="font-bold text-slate-500">Searching global catalog...</p>
              </div>
            ) : (drugResults?.drugs && drugResults.drugs.length > 0) ? (
              drugResults.drugs.map((drug: any) => (
                <button
                  key={drug.id}
                  onClick={() => handleDrugSelect(drug)}
                  className="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm text-left hover:border-primary/30 hover:shadow-xl hover:-translate-y-1 transition-all group"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400 group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                      <LayoutGrid className="w-6 h-6" />
                    </div>
                    <ArrowRight className="w-5 h-5 text-slate-200 group-hover:text-primary transition-all" />
                  </div>
                  <h3 className="text-xl font-black text-slate-900 leading-tight">{drug.brand_name || drug.generic_name}</h3>
                  <p className="text-sm font-bold text-slate-400 mt-1 uppercase tracking-wider">{drug.manufacturer}</p>
                  
                  <div className="flex flex-wrap gap-2 mt-6">
                    {drug.country_codes?.map((cc: string) => (
                      <span key={cc} className="px-2 py-1 bg-slate-50 text-[10px] font-black rounded-lg border border-slate-100">{cc}</span>
                    ))}
                  </div>
                </button>
              ))
            ) : searchQuery ? (
              <div className="col-span-2 py-20 bg-slate-50 rounded-[2.5rem] border-2 border-dashed border-slate-200 text-center">
                <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <h3 className="text-xl font-black text-slate-900">No matches found</h3>
                <p className="text-slate-500 font-medium">Try searching for a generic name or a different product.</p>
              </div>
            ) : (
              <div className="col-span-2 py-20 text-center">
                <p className="text-slate-400 font-bold">Start typing to search the regulatory database</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step 2: Country Selection */}
      {step === 2 && (
        <div className="space-y-8 animate-fade-in">
          <div className="bg-white p-10 rounded-[2.5rem] border border-slate-100 shadow-sm space-y-8">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <h2 className="text-2xl font-black text-slate-900">Jurisdiction Selection</h2>
                <p className="text-slate-500 font-medium mt-1">Select the countries you want to compare for {selectedDrug?.brand_name}</p>
              </div>
              <div className={cn(
                "px-4 py-2 rounded-xl text-xs font-black transition-all",
                selectedCountries.length >= 2 ? "bg-emerald-50 text-emerald-600 border border-emerald-100" : "bg-amber-50 text-amber-600 border border-amber-100"
              )}>
                {selectedCountries.length < 2 
                  ? `Select ${2 - selectedCountries.length} more region${selectedCountries.length === 1 ? "" : "s"} to compare`
                  : `${selectedCountries.length} Regions Selected`}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {selectedDrug?.country_codes?.map((cc: string) => (
                <button
                  key={cc}
                  onClick={() => toggleCountry(cc)}
                  className={cn(
                    "flex items-center gap-4 p-5 rounded-2xl border transition-all text-left h-full",
                    selectedCountries.includes(cc) 
                      ? "bg-primary/5 border-primary shadow-sm ring-4 ring-primary/5" 
                      : "bg-white border-slate-100 hover:border-slate-300"
                  )}
                >
                  <div className={cn(
                    "w-10 h-10 rounded-xl flex items-center justify-center font-black text-sm shrink-0",
                    selectedCountries.includes(cc) ? "bg-primary text-white" : "bg-slate-100 text-slate-400"
                  )}>
                    {cc}
                  </div>
                  <span className={cn(
                    "font-bold transition-colors leading-tight",
                    selectedCountries.includes(cc) ? "text-primary" : "text-slate-600"
                  )}>
                    {COUNTRY_NAMES[cc] || cc}
                  </span>
                  {selectedCountries.includes(cc) && <CheckCircle2 className="w-5 h-5 text-primary ml-auto shrink-0" />}
                </button>
              ))}
            </div>

            <div className="pt-8 border-t border-slate-50 flex items-center justify-between gap-4 flex-wrap">
              <button 
                onClick={() => setStep(1)}
                className="px-8 py-4 rounded-2xl font-black text-slate-500 hover:bg-slate-50 transition-all"
              >
                Back to Search
              </button>
              <div className="flex items-center gap-4">
                {selectedCountries.length === 1 && (
                  <span className="text-xs font-bold text-amber-500 animate-pulse">
                    Please select one more region
                  </span>
                )}
                <button 
                  disabled={selectedCountries.length < 2}
                  onClick={() => setStep(3)}
                  className="bg-primary text-white px-10 py-4 rounded-2xl font-black transition-all hover:scale-105 shadow-lg shadow-primary/25 disabled:opacity-50 disabled:scale-100 disabled:cursor-not-allowed"
                >
                  Continue to Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Section Selection */}
      {step === 3 && (
        <div className="space-y-8 animate-fade-in">
          <div className="bg-white p-10 rounded-[2.5rem] border border-slate-100 shadow-sm space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-black text-slate-900">Alignment Scope</h2>
                <p className="text-slate-500 font-medium mt-1">Configure which technical sections to analyze for discrepancies</p>
              </div>
              <button 
                onClick={() => setSelectedSections(COMPARE_SECTIONS)}
                className="text-xs font-black text-primary uppercase tracking-widest hover:underline"
              >
                Select All Sections
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {COMPARE_SECTIONS.map((section) => (
                <button
                  key={section}
                  onClick={() => toggleSection(section)}
                  className={cn(
                    "flex items-center gap-3 p-4 rounded-xl border text-left transition-all",
                    selectedSections.includes(section) 
                      ? "bg-slate-900 border-slate-900 shadow-md ring-4 ring-slate-900/5" 
                      : "bg-white border-slate-100 hover:border-slate-300"
                  )}
                >
                  <div className={cn(
                    "w-5 h-5 rounded flex items-center justify-center transition-colors",
                    selectedSections.includes(section) ? "bg-primary text-white" : "bg-slate-200"
                  )}>
                    {selectedSections.includes(section) && <CheckCircle2 className="w-3.5 h-3.5" />}
                  </div>
                  <span className={cn(
                    "text-xs font-bold transition-colors",
                    selectedSections.includes(section) ? "text-white" : "text-slate-600"
                  )}>
                    {section}
                  </span>
                </button>
              ))}
            </div>

            <div className="pt-8 border-t border-slate-50 flex items-center justify-between">
              <button 
                onClick={() => setStep(2)}
                className="px-8 py-4 rounded-2xl font-black text-slate-500 hover:bg-slate-50 transition-all"
              >
                Adjust Regions
              </button>
              <button 
                onClick={handleCompare}
                className="bg-primary text-white px-10 py-4 rounded-2xl font-black transition-all hover:scale-105 shadow-lg shadow-primary/25 flex items-center gap-3"
              >
                <Zap className="w-5 h-5 fill-current" />
                Launch Alignment Engine
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompareWizardPage;
