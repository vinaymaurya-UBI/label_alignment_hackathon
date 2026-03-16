import React from "react";
import { 
  History as HistoryIcon, 
  Search, 
  FileText, 
  RefreshCw, 
  ArrowRight,
  Clock,
  Eye,
  Loader2,
  Inbox,
  Download,
  Columns
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "../lib/utils";
import { useActivity, ActivityLog } from "../hooks/useActivity";

// Professional relative time formatter with UTC correction
const formatTime = (dateString: string) => {
  // Append Z if missing to treat as UTC from backend
  const normalizedDate = dateString.endsWith('Z') ? dateString : dateString + 'Z';
  const date = new Date(normalizedDate);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 0) return 'Just now'; // Handle slight clock drift
  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
};

const HistoryItem = ({ log }: { log: ActivityLog }) => {
  const navigate = useNavigate();
  const { type, title, subtitle, created_at, status, meta } = log;
  
  const getIcon = () => {
    switch (type) {
      case 'report': return <FileText className="w-5 h-5 text-blue-600" />;
      case 'search': return <Search className="w-5 h-5 text-indigo-600" />;
      case 'sync': return <RefreshCw className="w-5 h-5 text-emerald-600" />;
      case 'view': return <Eye className="w-5 h-5 text-amber-600" />;
      case 'export': return <Download className="w-5 h-5 text-rose-600" />;
      case 'compare': return <Columns className="w-5 h-5 text-violet-600" />;
      default: return <Clock className="w-5 h-5 text-slate-600" />;
    }
  };

  const getBg = () => {
    switch (type) {
      case 'report': return "bg-blue-50";
      case 'search': return "bg-indigo-50";
      case 'sync': return "bg-emerald-50";
      case 'view': return "bg-amber-50";
      case 'export': return "bg-rose-50";
      case 'compare': return "bg-violet-50";
      default: return "bg-slate-50";
    }
  };

  const handleNavigate = () => {
    if ((type === 'view' || type === 'compare') && meta?.drug_id) {
      navigate(`/drugs/${meta.drug_id}`);
    } else if (type === 'report' && meta?.drug_id) {
      navigate(`/reports/${meta.drug_id}`);
    } else if (type === 'export' && meta?.drug_id) {
      navigate(`/reports/${meta.drug_id}`);
    } else if (type === 'search' && meta?.query) {
      navigate(`/?q=${encodeURIComponent(meta.query)}`);
    }
  };

  const hasLink = (meta?.drug_id) || (type === 'search' && meta?.query);

  return (
    <div className="flex gap-6 group relative pb-10 last:pb-0 text-left">
      <div className="absolute left-[26px] top-12 bottom-0 w-0.5 bg-slate-100 group-last:hidden"></div>
      
      <div className={cn("w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 z-10 transition-all duration-300 group-hover:scale-110 shadow-sm", getBg())}>
        {getIcon()}
      </div>

      <div className="flex-1 pt-1">
        <div className="flex justify-between items-start mb-2">
          <div>
            <h4 className="text-lg font-black text-slate-900 group-hover:text-primary transition-colors">{title}</h4>
            <p className="text-sm font-bold text-slate-500 mt-0.5">{subtitle}</p>
          </div>
          <div className="text-right">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest block">{formatTime(created_at)}</span>
            {status && (
              <span className="inline-block mt-2 px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200/50">
                {status}
              </span>
            )}
          </div>
        </div>
        
        {hasLink && (
          <div className="flex items-center gap-4 mt-4">
            <button 
              onClick={handleNavigate}
              className="flex items-center gap-2 text-xs font-bold text-slate-900 hover:text-primary transition-all group/btn"
            >
              <span className="border-b-2 border-slate-200 group-hover/btn:border-primary pb-0.5">
                Revisit Activity
              </span>
              <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-1" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const HistoryPage = () => {
  const { data: logs, isLoading, clearActivity, isClearing } = useActivity(50);

  return (
    <div className="max-w-4xl space-y-10">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-2 text-left">
          <h1 className="text-4xl font-black text-slate-900 tracking-tight flex items-center gap-4">
            Intelligence Log
            <HistoryIcon className="w-8 h-8 text-primary" />
          </h1>
          <p className="text-slate-500 font-medium">Professional record of regulatory actions, analysis, and alignment checks</p>
        </div>
        <button 
          onClick={() => {
            if (window.confirm("Are you sure you want to clear the entire intelligence log? This action cannot be undone.")) {
              clearActivity();
            }
          }}
          disabled={isClearing || !logs?.length}
          className="bg-white border border-slate-200 px-6 py-3 rounded-2xl text-sm font-bold text-slate-600 hover:bg-rose-50 hover:text-rose-600 hover:border-rose-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-sm"
        >
          {isClearing && <Loader2 className="w-4 h-4 animate-spin" />}
          Clear Activity Log
        </button>
      </div>

      <div className="bg-white p-12 rounded-[3rem] border border-slate-100 shadow-sm min-h-[400px] flex flex-col">
        {isLoading ? (
          <div className="flex-1 flex items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-primary animate-spin" />
          </div>
        ) : !logs || logs.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-400 space-y-4 py-20">
            <div className="p-6 bg-slate-50 rounded-full">
              <Inbox className="w-12 h-12" />
            </div>
            <div className="text-center">
              <p className="font-bold uppercase tracking-widest text-xs">Intelligence Log is Empty</p>
              <p className="text-sm font-medium mt-1">Start by searching the catalog or performing a regulatory comparison.</p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {logs.map((log) => (
              <HistoryItem key={log.id} log={log} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;
