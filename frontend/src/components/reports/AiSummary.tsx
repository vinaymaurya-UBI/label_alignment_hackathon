import React, { useState, useEffect } from "react";
import { Sparkles, ShieldCheck, RefreshCw, AlertCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import useReportStream from "../../hooks/useReportStream";
import { cn } from "../../lib/utils";

interface Props {
  drugId: string;
  initialSummary?: string;
}

const AiSummary = ({ drugId, initialSummary }: Props) => {
  const [summary, setSummary] = useState(initialSummary || "Click generate to analyze regulatory text and identify key insights across jurisdictions.");

  const { status, message, error, start } = useReportStream({
    drugId,
    onComplete: (markdown) => {
      // Extract Regulatory AI Insight or Executive Summary
      const insightMatch = markdown.match(/(?:#+ )?Regulatory AI Insight[\s\S]*?(?=\n#+|$)/i);
      const summaryMatch = markdown.match(/# Executive Summary\n+([\s\S]*?)(?=\n#|$)/i);
      
      if (insightMatch) {
        setSummary(insightMatch[0].trim());
      } else if (summaryMatch && summaryMatch[1]) {
        setSummary(summaryMatch[1].trim());
      } else {
        setSummary(markdown.slice(0, 800) + (markdown.length > 800 ? "..." : ""));
      }
    }
  });

  const isGenerating = status === "starting" || status === "generating";

  const handleGenerate = () => {
    start();
  };

  return (
    <div className="bg-white rounded-[2rem] border border-slate-100 shadow-sm overflow-hidden flex flex-col h-full">
      <div className="p-6 border-b border-slate-50 bg-slate-50/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900 leading-none">Regulatory AI Insight</h3>
            <div className="flex items-center gap-1.5 mt-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
              <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider">Verified by LLM</span>
            </div>
          </div>
        </div>
        
        <button 
          onClick={handleGenerate}
          disabled={isGenerating}
          className={cn(
            "p-2.5 rounded-xl transition-all border",
            isGenerating 
              ? "bg-slate-100 text-slate-400 border-slate-100 cursor-not-allowed" 
              : "bg-white text-slate-600 border-slate-200 hover:border-primary hover:text-primary shadow-sm"
          )}
        >
          <RefreshCw className={cn("w-4 h-4", isGenerating && "animate-spin")} />
        </button>
      </div>

      <div className="p-8 flex-1 relative flex flex-col">
        {isGenerating ? (
          <div className="space-y-4 flex-1">
            <div className="h-4 bg-slate-100 rounded-full w-full animate-pulse"></div>
            <div className="h-4 bg-slate-100 rounded-full w-[90%] animate-pulse"></div>
            <div className="h-4 bg-slate-100 rounded-full w-[95%] animate-pulse"></div>
            <div className="h-4 bg-slate-100 rounded-full w-[80%] animate-pulse"></div>
            <p className="text-xs font-bold text-blue-500 mt-4 animate-pulse">{message || "Analyzing jurisdictions..."}</p>
          </div>
        ) : error ? (
           <div className="flex-1 text-red-600 font-medium">
             Error: {error}
           </div>
        ) : (
          <div className="prose prose-slate max-w-none flex-1">
            <div className="text-slate-600 leading-relaxed font-medium">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {summary}
              </ReactMarkdown>
            </div>
          </div>
        )}

        <div className="mt-8 flex items-center gap-2 px-4 py-3 bg-blue-50/50 rounded-2xl border border-blue-100/50 shrink-0">
          <AlertCircle className="w-4 h-4 text-blue-500 shrink-0" />
          <p className="text-[11px] text-blue-600 font-bold leading-tight">
            AI analysis is for guidance only. Always refer to official regulatory documents for final verification.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AiSummary;
