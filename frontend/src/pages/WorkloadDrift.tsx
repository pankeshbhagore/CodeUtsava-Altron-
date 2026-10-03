import React, { useEffect, useState } from 'react';
import { Activity, Clock } from 'lucide-react';
import { apiClient } from '../api/client';

const WorkloadDrift = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [drift, setDrift] = useState<any>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await apiClient.getDashboardMetrics();
        setMetrics(data);
        const driftData = await apiClient.getWorkloadDrift();
        setDrift(driftData);
      } catch (e) {
        console.error(e);
      }
    };
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold flex items-center text-slate-800 dark:text-slate-100">
            7. Workload Drift Analysis
          </h2>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center">
          <p className="text-sm text-slate-500 mb-2">Drift Score</p>
          <div className="relative w-32 h-32 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" stroke="#f1f5f9" strokeWidth="12" fill="none" />
              <circle cx="50" cy="50" r="40" stroke={drift?.drift_score > 0.3 ? "#ef4444" : "#10b981"} strokeWidth="12" fill="none" strokeDasharray={`${(drift?.drift_score || 0) * 251} 251`} className="transition-all duration-1000 ease-out" />
            </svg>
            <div className="absolute text-center">
              <p className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">{Math.round((drift?.drift_score || 0) * 100)}%</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-center">
          <p className="text-sm text-slate-500 mb-2">Confidence Impact</p>
          <p className="text-3xl font-bold text-red-500">-{Math.round((drift?.confidence_impact || 0) * 100)}%</p>
          <p className="text-xs text-slate-400 mt-2">Reduction in AI model confidence</p>
        </div>
        <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-center col-span-1 md:col-span-2">
          <p className="text-sm text-slate-500 mb-2">AI Summary</p>
          <p className="text-slate-800 dark:text-slate-200 text-lg font-medium">{drift?.summary || 'Analyzing workload patterns...'}</p>
        </div>
      </div>

      {drift?.drift_score > 0 && (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
          <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-6 border-b border-slate-100 pb-2">Shift Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold text-slate-600 mb-3">New Tables Accessed</h4>
              <ul className="list-disc pl-5 space-y-1">
                {(drift?.new_tables || []).map((t: string, i: number) => (
                  <li key={i} className="text-slate-700 dark:text-slate-300 font-mono text-sm">{t}</li>
                ))}
                {drift?.new_tables?.length === 0 && <span className="text-slate-400 text-sm">None detected</span>}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-slate-600 mb-3">New Filter Patterns</h4>
              <ul className="list-disc pl-5 space-y-1">
                {(drift?.new_filters || []).map((f: string, i: number) => (
                  <li key={i} className="text-slate-700 dark:text-slate-300 font-mono text-sm">{f}</li>
                ))}
                {drift?.new_filters?.length === 0 && <span className="text-slate-400 text-sm">None detected</span>}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-slate-600 mb-3">New Join Patterns</h4>
              <ul className="list-disc pl-5 space-y-1">
                {(drift?.new_joins || []).map((j: string, i: number) => (
                  <li key={i} className="text-slate-700 dark:text-slate-300 font-mono text-sm">{j}</li>
                ))}
                {drift?.new_joins?.length === 0 && <span className="text-slate-400 text-sm">None detected</span>}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkloadDrift;


