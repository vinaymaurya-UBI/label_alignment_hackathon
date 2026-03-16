import React from "react";
import { 
  BarChart3, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Globe2,
  PieChart,
  ArrowUpRight,
  Loader2
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "../lib/utils";
import { useAnalytics } from "../hooks/useActivity";

const AnalyticsCard = ({ title, value, subtitle, icon: Icon, color }: any) => (
  <div className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-glow transition-all duration-500 group">
    <div className="flex justify-between items-start mb-6">
      <div className={cn("p-4 rounded-2xl transition-transform duration-500 group-hover:scale-110", color)}>
        <Icon className="w-6 h-6" />
      </div>
    </div>
    <h3 className="text-4xl font-black text-slate-900 tracking-tight mb-1">{value}</h3>
    <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">{title}</p>
    {subtitle && <p className="text-xs text-slate-400 mt-2 font-medium">{subtitle}</p>}
  </div>
);

const AnalyticsPage = () => {
  const navigate = useNavigate();
  const { data: analytics, isLoading } = useAnalytics();

  if (isLoading) {
    return (
      <div className="h-[60vh] flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-primary animate-spin" />
      </div>
    );
  }

  const { counts, alignment_metrics, labels_per_country } = analytics || {};

  return (
    <div className="space-y-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-black text-slate-900 tracking-tight">Portfolio Alignment Health</h1>
        <p className="text-slate-500 font-medium">Real-time mapping of label density and jurisdictional coverage across your drug assets</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <AnalyticsCard 
          title="Analysis Checks" 
          value={alignment_metrics?.checks_performed || 0} 
          subtitle="Total AI reports generated"
          icon={TrendingUp} 
          color="bg-blue-50 text-blue-600" 
        />
        <AnalyticsCard 
          title="Alignment Score" 
          value={`${alignment_metrics?.alignment_score || 0}%`} 
          subtitle="Confidence in cross-market parity"
          icon={CheckCircle2} 
          color="bg-emerald-50 text-emerald-600" 
        />
        <AnalyticsCard 
          title="Active Markets" 
          value={counts?.jurisdictions || 0} 
          subtitle="Countries with verified data"
          icon={Globe2} 
          color="bg-indigo-50 text-indigo-600" 
        />
        <AnalyticsCard 
          title="Data Granularity" 
          value={alignment_metrics?.avg_data_depth || 0} 
          subtitle="Avg sections analyzed per drug"
          icon={BarChart3} 
          color="bg-amber-50 text-amber-600" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm relative overflow-hidden group">
          <div className="flex items-center justify-between mb-10 relative z-10">
            <h3 className="text-2xl font-black text-slate-900 flex items-center gap-3">
              <PieChart className="w-6 h-6 text-primary" />
              Jurisdictional Balance
            </h3>
            <button 
              onClick={() => navigate('/activity-log')}
              className="text-xs font-bold text-slate-400 hover:text-primary transition-colors uppercase tracking-widest"
            >
              View Compliance Log
            </button>
          </div>
          
          <div className="space-y-6 relative z-10">
            <p className="text-sm text-slate-500 font-medium mb-4 italic">
              Distribution of regulatory labels currently active in the intelligence engine:
            </p>
            {Object.entries(labels_per_country || {}).map(([cc, count]: any) => {
              const percentage = Math.round((count / (counts?.labels || 1)) * 100);
              return (
                <div key={cc} className="space-y-2">
                  <div className="flex justify-between text-sm font-bold">
                    <span className="text-slate-600 uppercase tracking-widest">{cc} Market</span>
                    <span className="text-slate-900">{count} labels ({percentage}%)</span>
                  </div>
                  <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-1000 bg-primary/60" 
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-slate-900 p-10 rounded-[3rem] border border-slate-800 shadow-2xl relative overflow-hidden text-white group">
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-10">
              <h3 className="text-2xl font-black flex items-center gap-3 text-white">
                <AlertTriangle className="w-6 h-6 text-amber-400" />
                Understanding These Metrics
              </h3>
            </div>
            
            <div className="space-y-6">
              <div className="bg-white/5 border border-white/10 p-5 rounded-2xl">
                <h4 className="text-sm font-black text-blue-400 uppercase tracking-widest mb-1">Portfolio Health</h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  The <strong>Alignment Score</strong> measures how well synchronized your drug portfolio is across jurisdictions. Lower scores indicate high volume of manual reports, suggesting detected variations.
                </p>
              </div>

              <div className="bg-white/5 border border-white/10 p-5 rounded-2xl">
                <h4 className="text-sm font-black text-amber-400 uppercase tracking-widest mb-1">Data Granularity</h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Represents the average number of medical sections (Dosage, Warnings, etc.) per label. Higher numbers indicate more comprehensive regulatory data ingestion.
                </p>
              </div>

              <div className="bg-white/5 border border-white/10 p-5 rounded-2xl">
                <h4 className="text-sm font-black text-emerald-400 uppercase tracking-widest mb-1">Verification Level</h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Reflects the frequency of AI-driven deep-dives. Increasing this activity helps catch subtle linguistic discrepancies in safety warnings.
                </p>
              </div>
            </div>
          </div>
          <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-br from-blue-500/5 to-transparent pointer-events-none"></div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
