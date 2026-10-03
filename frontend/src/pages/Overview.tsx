import React, { useEffect, useState } from 'react';
import { Activity, ShieldCheck, Database, Zap, ArrowRight, Clock } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import { apiClient } from '../api/client';

const Overview = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [recs, setRecs] = useState<any[]>([]);
  const [recentQueries, setRecentQueries] = useState<any[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const mData = await apiClient.getDashboardMetrics();
        setMetrics(mData);
        const rData = await apiClient.getRecommendations();
        setRecs(rData?.recommendations || []);
        const qData = await apiClient.getRecentQueries();
        setRecentQueries(qData?.queries || []);
      } catch (e) {
        console.error(e);
      }
    };
    loadData();
    // Poll every 10 seconds for real-time feel
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard title="System Health" value={metrics ? `${metrics.health_score}%` : '---'} icon={<Activity className="text-green-500" />} />
        <MetricCard title="Queries Analyzed" value={metrics ? metrics.total_queries_analyzed.toLocaleString() : '---'} icon={<Database className="text-blue-500" />} />
        <MetricCard title="Avg Improvement" value={metrics ? `${Math.round(metrics.avg_improvement_pct)}%` : '---'} icon={<Zap className="text-yellow-500" />} />
        <MetricCard title="Privacy Status" value={metrics ? metrics.privacy_status : '---'} icon={<ShieldCheck className="text-emerald-500" />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Real-time DB Queries Table */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
          <h3 className="text-lg font-medium mb-4 flex items-center justify-between">
            <span className="flex items-center"><Database className="w-5 h-5 mr-2 text-blue-500"/> Live Slow Queries (PostgreSQL)</span>
            <span className="flex items-center text-xs text-green-500 font-bold"><span className="w-2 h-2 rounded-full bg-green-500 animate-pulse mr-1"></span> LIVE</span>
          </h3>
          <div className="space-y-3">
            {recentQueries.length === 0 ? (
              <p className="text-slate-500 text-sm">No live queries detected in DB yet.</p>
            ) : (
              recentQueries.map((q, i) => (
                <div key={i} className="p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-[#0d1117] flex justify-between items-start">
                  <code className="text-xs text-slate-600 dark:text-slate-400 font-mono flex-1">{q.sql}</code>
                  <div className="ml-4 flex flex-col items-end">
                    <span className="text-xs font-bold text-red-500">{q.time_ms.toFixed(1)} ms</span>
                    <span className="text-[10px] text-slate-400 flex items-center mt-1"><Clock className="w-3 h-3 mr-1"/> Just now</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent AI Recommendations */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
          <h3 className="text-lg font-medium mb-4 flex items-center justify-between">
            <span>Recent AI Recommendations</span>
            <a href="/recommendations" className="text-sm text-blue-500 hover:underline flex items-center">
              View All <ArrowRight className="w-4 h-4 ml-1" />
            </a>
          </h3>
          {recs.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-sm">
              No recommendations generated yet. Use the Query Analyzer to test a query!
            </div>
          ) : (
            <div className="space-y-3">
              {recs.slice(0, 4).map((rec, i) => (
                <div key={i} className="flex justify-between items-center p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-[#0d1117]">
                  <div>
                    <h4 className="font-bold text-sm text-slate-800 dark:text-slate-200">{rec.type}</h4>
                    <p className="text-xs text-slate-500 mt-1">Table: <span className="font-mono text-blue-600 dark:text-blue-400">{rec.table}</span></p>
                  </div>
                  <div className="text-right flex flex-col items-end">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${rec.status === 'simulated' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'}`}>
                      {rec.status.toUpperCase()}
                    </span>
                    <span className="text-xs text-emerald-600 font-bold mt-2">-{rec.estimated_improvement_pct}% Time</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Overview;
