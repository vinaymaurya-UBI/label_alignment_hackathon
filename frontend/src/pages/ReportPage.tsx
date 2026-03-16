import React, { useState } from "react";
import { useParams, Link as RouterLink } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { 
  ChevronRight, 
  Zap, 
  Copy, 
  FileDown, 
  Activity, 
  AlertCircle,
  Sparkles,
  CheckCircle2,
  RefreshCw,
  Layout
} from "lucide-react";
import { 
  ChevronRight as ChevronRightIcon, 
  Zap as ZapIcon, 
  Copy as CopyIcon, 
  FileDown as FileDownIcon, 
  Activity as ActivityIcon, 
  AlertCircle as AlertCircleIcon,
  Sparkles as SparklesIcon,
  CheckCircle2 as CheckCircle2Icon,
  RefreshCw as RefreshCwIcon,
  Layout as LayoutIcon
} from "lucide-react";
import useReportStream from "../hooks/useReportStream";
import { api } from "../services/api";
import { cn } from "../lib/utils";

const ReportPage = () => {
  const { drugId } = useParams<{ drugId: string }>();
  const [markdown, setMarkdown] = useState("");
  const [toast, setToast] = useState("");
  const [docxLoading, setDocxLoading] = useState(false);
  const [started, setStarted] = useState(false);

  const { status, progress, message, error, start } = useReportStream({
    drugId: drugId ?? "",
    onComplete: setMarkdown,
  });

  const handleStart = () => {
    setStarted(true);
    setMarkdown("");
    start();
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(markdown);
    setToast("Report copied to clipboard");
    setTimeout(() => setToast(""), 3000);
  };

  const handleDownloadTxt = () => {
    const blob = new Blob([markdown], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `labelalign_report_${drugId}.txt`;
    a.click();
  };

  const handleDownloadDocx = async () => {
    if (!markdown) return;
    setDocxLoading(true);
    try {
      const res = await api.post(
        `/api/v1/ai/download-docx/${drugId}`,
        { report: markdown },
        { responseType: "blob" }
      );
      const blob = new Blob([res.data], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `labelalign_report_${drugId}.docx`;
      a.click();
    } catch {
      setToast("Failed to download DOCX");
      setTimeout(() => setToast(""), 3000);
    } finally {
      setDocxLoading(false);
    }
  };

  const isRunning = status === "starting" || status === "generating";

  return (
    <div className="space-y-10 pb-20">
      {/* Breadcrumbs */}
      <nav className="flex items-center gap-2 text-sm font-bold text-slate-400">
        <RouterLink to="/" className="hover:text-primary transition-colors">Drugs</RouterLink>
        <ChevronRightIcon className="w-4 h-4" />
        {drugId && (
          <RouterLink to={`/drugs/${drugId}`} className="hover:text-primary transition-colors">Drug Detail</RouterLink>
        )}
        <ChevronRightIcon className="w-4 h-4" />
        <span className="text-slate-900">AI Intelligence Report</span>
      </nav>

      {/* Hero Header */}
      <div className="bg-slate-900 rounded-[3rem] p-10 text-white relative overflow-hidden shadow-2xl">
        <div className="relative z-10">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
            <div className="space-y-6 max-w-2xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full text-[10px] font-black uppercase tracking-widest border border-white/10">
                <SparklesIcon className="w-3.5 h-3.5 text-blue-400" />
                Powered by NeuroNext AI
              </div>
              <h1 className="text-4xl font-black tracking-tight leading-tight">Regulatory Intelligence <span className="text-blue-400">Report</span></h1>
              <p className="text-lg text-slate-300 font-medium">
                Comprehensive cross-jurisdictional alignment analysis and automated discrepancy detection for global regulatory compliance.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <button 
                onClick={handleStart}
                disabled={isRunning}
                className={cn(
                  "flex items-center gap-3 px-8 py-4 rounded-2xl font-black text-sm transition-all shadow-lg",
                  isRunning 
                    ? "bg-slate-700 text-slate-400 cursor-not-allowed" 
                    : "bg-primary text-white hover:scale-105 hover:shadow-primary/20"
                )}
              >
                {isRunning ? (
                  <>
                    <RefreshCwIcon className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <ZapIcon className="w-4 h-4 fill-current" />
                    {started ? "Regenerate Intelligence" : "Start AI Analysis"}
                  </>
                )}
              </button>

              {markdown && (
                <div className="flex gap-2">
                  <button 
                    onClick={handleCopy}
                    className="p-4 bg-white/10 text-white rounded-2xl hover:bg-white/20 transition-all border border-white/10"
                    title="Copy to clipboard"
                  >
                    <CopyIcon className="w-5 h-5" />
                  </button>
                  <button 
                    onClick={handleDownloadDocx}
                    disabled={docxLoading}
                    className="flex items-center gap-2 px-6 py-4 bg-white text-slate-900 rounded-2xl font-black text-sm hover:bg-slate-100 transition-all shadow-lg border border-slate-200"
                  >
                    {docxLoading ? <RefreshCwIcon className="w-4 h-4 animate-spin" /> : <FileDownIcon className="w-4 h-4" />}
                    DOCX
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-[120px] -translate-y-1/2 translate-x-1/2"></div>
      </div>

      {/* Progress & Status */}
      {isRunning && (
        <div className="max-w-3xl mx-auto space-y-6 py-10 text-center animate-fade-in">
          <div className="inline-flex items-center gap-3 px-4 py-2 bg-blue-50 text-blue-600 rounded-full text-sm font-black">
            <ActivityIcon className="w-4 h-4 animate-pulse" />
            {message}
          </div>
          
          <div className="relative h-4 bg-slate-100 rounded-full overflow-hidden border border-slate-200 shadow-inner">
            <div 
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-primary to-blue-400 transition-all duration-500 rounded-full"
              style={{ width: `${progress > 0 ? progress : 40}%` }}
            >
              <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-10"></div>
            </div>
          </div>
          
          <p className="text-slate-500 font-medium italic">
            Scanning FDA, EMA, and PMDA databases for technical discrepancies...
          </p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-100 p-6 rounded-3xl flex items-center gap-4 text-red-600 max-w-3xl mx-auto">
          <AlertCircleIcon className="w-6 h-6" />
          <p className="font-bold">{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!started && !markdown && (
        <div className="bg-white border-2 border-dashed border-slate-200 p-20 rounded-[3rem] text-center max-w-4xl mx-auto">
          <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <LayoutIcon className="w-10 h-10 text-slate-300" />
          </div>
          <h3 className="text-2xl font-black text-slate-900 tracking-tight">Ready for Generation</h3>
          <p className="text-slate-500 font-medium mt-2 max-w-md mx-auto">
            Our AI engine will analyze all available jurisdictional labels to create a unified intelligence report.
          </p>
          <button 
            onClick={handleStart}
            className="mt-8 px-8 py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all"
          >
            Launch Intelligence Engine
          </button>
        </div>
      )}

      {/* Report Content */}
      {markdown && (
        <div className="max-w-5xl mx-auto bg-white rounded-[3rem] border border-slate-100 shadow-xl overflow-hidden animate-scale-up">
          <div className="px-10 py-8 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle2Icon className="w-6 h-6 text-emerald-500" />
              <h2 className="text-xl font-black text-slate-900">Intelligence Summary</h2>
            </div>
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest bg-white px-3 py-1 rounded-full border border-slate-100">
              Generated: {new Date().toLocaleDateString()}
            </span>
          </div>
          
          <div className="p-10 md:p-16">
            <article className="prose prose-slate max-w-none 
              prose-h1:text-4xl prose-h1:font-black prose-h1:tracking-tight prose-h1:border-b-4 prose-h1:border-blue-50 prose-h1:pb-4 prose-h1:mb-8
              prose-h2:text-2xl prose-h2:font-black prose-h2:text-primary prose-h2:flex prose-h2:items-center prose-h2:gap-3 prose-h2:mt-12
              prose-h3:text-xl prose-h3:font-black prose-h3:text-slate-800 prose-h3:mt-8
              prose-p:text-slate-600 prose-p:leading-relaxed prose-p:text-lg prose-p:font-medium
              prose-li:text-slate-600 prose-li:font-medium prose-li:text-lg
              prose-table:w-full prose-table:border-collapse prose-table:rounded-2xl prose-table:overflow-hidden prose-table:border prose-table:border-slate-100
              prose-th:bg-slate-900 prose-th:text-white prose-th:px-6 prose-th:py-4 prose-th:font-black prose-th:text-xs prose-th:uppercase prose-th:tracking-widest prose-th:text-left
              prose-td:px-6 prose-td:py-4 prose-td:border-b prose-td:border-slate-50 prose-td:text-sm prose-td:text-slate-600
              prose-blockquote:border-l-8 prose-blockquote:border-primary prose-blockquote:bg-blue-50/50 prose-blockquote:rounded-r-2xl prose-blockquote:px-8 prose-blockquote:py-6 prose-blockquote:italic prose-blockquote:text-blue-700
            ">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {markdown}
              </ReactMarkdown>
            </article>
          </div>

          <div className="px-10 py-8 bg-slate-50 border-t border-slate-100 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
              <p className="text-xs font-black text-slate-400 uppercase tracking-widest">End of Intelligence Report</p>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={handleCopy}
                className="flex items-center gap-2 px-6 py-2 bg-white text-slate-600 border border-slate-200 rounded-xl text-xs font-black hover:border-primary hover:text-primary transition-all shadow-sm"
              >
                <CopyIcon className="w-3.5 h-3.5" />
                Copy Text
              </button>
              <button 
                onClick={handleDownloadDocx}
                className="flex items-center gap-2 px-6 py-2 bg-white text-slate-600 border border-slate-200 rounded-xl text-xs font-black hover:border-primary hover:text-primary transition-all shadow-sm"
              >
                {docxLoading ? <RefreshCwIcon className="w-3.5 h-3.5" /> : <FileDownIcon className="w-3.5 h-3.5" />}
                DOCX
              </button>
              <button 
                onClick={handleDownloadTxt}
                className="flex items-center gap-2 px-6 py-2 bg-slate-900 text-white rounded-xl text-xs font-black hover:bg-slate-800 transition-all shadow-lg"
              >
                <FileDownIcon className="w-3.5 h-3.5" />
                Download TXT
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-10 left-1/2 -translate-x-1/2 bg-slate-900 text-white px-8 py-4 rounded-2xl font-bold shadow-2xl animate-fade-in flex items-center gap-3 z-50">
          <CheckCircle2Icon className="w-5 h-5 text-emerald-400" />
          {toast}
        </div>
      )}
    </div>
  );
};

export default ReportPage;
