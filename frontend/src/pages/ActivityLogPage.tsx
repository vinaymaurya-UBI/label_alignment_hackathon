import React from "react";
import { 
  FileSearch, 
  ArrowLeft,
  Filter,
  Download,
  MoreHorizontal,
  ExternalLink,
  Loader2,
  Inbox,
  FileText,
  Search,
  Eye,
  RefreshCw,
  Clock
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "../lib/utils";
import { useActivity, ActivityLog } from "../hooks/useActivity";

const LogRow = ({ log }: { log: ActivityLog }) => {
  const getIcon = () => {
    switch (log.type) {
      case 'report': return <FileText className="w-4 h-4 text-blue-600" />;
      case 'search': return <Search className="w-4 h-4 text-indigo-600" />;
      case 'sync': return <RefreshCw className="w-4 h-4 text-emerald-600" />;
      case 'view': return <Eye className="w-4 h-4 text-amber-600" />;
      default: return <Clock className="w-4 h-4 text-slate-600" />;
    }
  };

  const getTypeStyles = () => {
    switch (log.type) {
      case 'report': return "bg-blue-50 text-blue-600 border-blue-100";
      case 'search': return "bg-indigo-50 text-indigo-600 border-indigo-100";
      case 'sync': return "bg-emerald-50 text-emerald-600 border-emerald-100";
      default: return "bg-slate-50 text-slate-600 border-slate-100";
    }
  };

  return (
    <tr className="group border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
      <td className="py-5 pl-8">
        <div className="flex items-center gap-3">
          <div className={cn("p-2 rounded-lg border", getTypeStyles())}>
            {getIcon()}
          </div>
          <span className={cn("px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider border", getTypeStyles())}>
            {log.type}
          </span>
        </div>
      </td>
      <td className="py-5">
        <div className="flex flex-col">
          <span className="text-sm font-black text-slate-900">{log.title}</span>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest truncate max-w-xs">{log.subtitle}</span>
        </div>
      </td>
      <td className="py-5 text-sm font-bold text-slate-500">
        {new Date(log.created_at).toLocaleString()}
      </td>
      <td className="py-5">
        <div className="flex items-center gap-2">
          <span className="text-xs font-black uppercase tracking-wider text-slate-600 bg-slate-100 px-2 py-1 rounded-md">
            {log.status || 'Success'}
          </span>
        </div>
      </td>
      <td className="py-5 pr-8 text-right">
        <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button className="p-2 hover:bg-white rounded-lg border border-transparent hover:border-slate-200 transition-all text-slate-400 hover:text-primary">
            <ExternalLink className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-white rounded-lg border border-transparent hover:border-slate-200 transition-all text-slate-400 hover:text-slate-900">
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
      </td>
    </tr>
  );
};

const ActivityLogPage = () => {
  const navigate = useNavigate();
  const { data: logs, isLoading } = useActivity(100);

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-6">
        <button 
          onClick={() => navigate(-1)}
          className="p-3 bg-white border border-slate-200 rounded-2xl text-slate-400 hover:text-slate-900 hover:border-slate-300 transition-all shadow-sm"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">Compliance Log</h1>
          <p className="text-slate-500 font-medium">Detailed audit of all regulatory actions, searches, and data synchronizations</p>
        </div>
      </div>

      <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden min-h-[500px] flex flex-col">
        <div className="p-8 border-b border-slate-50 flex flex-wrap items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <FileSearch className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search log entries..." 
                className="pl-11 pr-6 py-3 bg-slate-50 border-none rounded-2xl text-sm font-medium focus:ring-2 focus:ring-primary/20 outline-none w-80"
              />
            </div>
            <button className="flex items-center gap-2 px-5 py-3 bg-slate-50 text-slate-600 rounded-2xl text-sm font-bold hover:bg-slate-100 transition-all">
              <Filter className="w-4 h-4" />
              Filter
            </button>
          </div>
          <button className="flex items-center gap-2 px-5 py-3 bg-slate-900 text-white rounded-2xl text-sm font-bold hover:bg-slate-800 transition-all shadow-lg shadow-slate-900/20">
            <Download className="w-4 h-4" />
            Export Audit Data
          </button>
        </div>

        <div className="flex-1 overflow-x-auto">
          {isLoading ? (
            <div className="h-full flex items-center justify-center p-20">
              <Loader2 className="w-12 h-12 text-primary animate-spin" />
            </div>
          ) : !logs || logs.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 p-20 space-y-4">
              <div className="p-6 bg-slate-50 rounded-full">
                <Inbox className="w-12 h-12" />
              </div>
              <p className="font-bold uppercase tracking-widest text-xs">No audit logs found</p>
            </div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/50">
                  <th className="py-4 pl-8 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Action Type</th>
                  <th className="py-4 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Activity Details</th>
                  <th className="py-4 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Timestamp</th>
                  <th className="py-4 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Status</th>
                  <th className="py-4 pr-8 text-right text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Actions</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <LogRow key={log.id} log={log} />
                ))}
              </tbody>
            </table>
          )}
        </div>
        
        <div className="p-8 bg-slate-50/30 border-t border-slate-50 text-center">
          <p className="text-sm font-bold text-slate-400">
            {logs ? `Showing ${logs.length} total entries` : 'No entries found'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ActivityLogPage;
