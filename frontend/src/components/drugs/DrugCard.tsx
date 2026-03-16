import React from "react";
import { Link as RouterLink } from "react-router-dom";
import { 
  Building2, 
  Globe2, 
  ChevronRight, 
  FileSearch, 
  Zap,
  ArrowRightLeft
} from "lucide-react";
import type { Drug } from "../../types";
import { cn } from "../../lib/utils";

interface Props {
  drug: Drug;
}

const COUNTRY_NAMES: Record<string, string> = {
  US: "USA",
  EU: "Europe",
  GB: "UK",
  CA: "Canada",
  JP: "Japan",
  AU: "Australia",
  IN: "India"
};

function DrugCard({ drug }: Props) {
  const name = drug.brand_name || drug.generic_name;
  const subtitle = drug.brand_name ? drug.generic_name : null;

  return (
    <RouterLink 
      to={`/drugs/${drug.id}`}
      className="card-glow flex flex-col h-full overflow-hidden group cursor-pointer transition-all hover:scale-[1.02]"
    >
      <div className="p-6 flex-1">
        <div className="flex justify-between items-start mb-4">
          {drug.therapeutic_area && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-primary/5 text-primary uppercase tracking-wider">
              {drug.therapeutic_area}
            </span>
          )}
        </div>

        <h3 className="text-lg font-black text-slate-900 leading-tight group-hover:text-primary transition-colors line-clamp-2" title={name}>
          {name}
        </h3>
        {subtitle && (
          <p className="text-xs font-semibold text-slate-400 mt-1 line-clamp-1">
            {subtitle}
          </p>
        )}

        <div className="mt-6 space-y-3">
          {drug.manufacturer && (
            <div className="flex items-center gap-2 text-slate-500">
              <Building2 className="w-3.5 h-3.5" />
              <span className="text-[11px] font-bold truncate">{drug.manufacturer}</span>
            </div>
          )}
          
          <div className="flex items-center gap-2">
            <Globe2 className="w-3.5 h-3.5 text-slate-400" />
            <div className="flex flex-wrap gap-1">
              {drug.country_codes.slice(0, 4).map((cc) => (
                <span 
                  key={cc} 
                  className="px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded text-[9px] font-black flex flex-col items-center min-w-[24px]"
                  title={COUNTRY_NAMES[cc] || cc}
                >
                  <span>{cc}</span>
                </span>
              ))}
              {drug.country_codes.length > 4 && (
                <span className="text-[9px] font-bold text-slate-400">
                  +{drug.country_codes.length - 4}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between gap-2 mt-auto">
        <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
          <RouterLink 
            to={`/drugs/${drug.id}`}
            className="p-2 text-slate-400 hover:text-primary hover:bg-white rounded-lg transition-all border border-transparent hover:border-slate-100"
            title="Details"
          >
            <ChevronRight className="w-4 h-4" />
          </RouterLink>
          <RouterLink 
            to={`/compare/${drug.id}`}
            className="p-2 text-slate-400 hover:text-primary hover:bg-white rounded-lg transition-all border border-transparent hover:border-slate-100"
            title="Compare"
          >
            <ArrowRightLeft className="w-4 h-4" />
          </RouterLink>
        </div>

        <div onClick={(e) => e.stopPropagation()}>
          <RouterLink 
            to={`/reports/${drug.id}`}
            className="flex items-center gap-2 px-4 py-2 bg-white text-slate-700 hover:bg-primary hover:text-white border border-slate-200 rounded-xl text-xs font-black transition-all shadow-sm hover:shadow-md hover:border-primary"
          >
            <Zap className="w-3.5 h-3.5 fill-current" />
            AI Report
          </RouterLink>
        </div>
      </div>
    </RouterLink>
  );
}

export default DrugCard;
