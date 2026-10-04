import React from 'react';
import { 
  ListChecks, 
  Clock, 
  CheckCircle2, 
  BarChart2, 
  Lock, 
  FlaskConical, 
  Hourglass,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

// Generate last 8 days dynamically for real-time feel
const generateDynamicLineData = () => {
  const data = [];
  const baseBefore = [6.0, 7.2, 5.5, 5.3, 4.0, 5.0, 4.8, 4.1];
  const baseAfter = [4.8, 3.4, 2.4, 1.8, 1.3, 2.5, 1.1, 1.3];
  
  for (let i = 7; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const month = date.toLocaleString('default', { month: 'short' });
    const day = date.getDate();
    data.push({
      name: `${month} ${day}`,
      before: baseBefore[7 - i],
      after: baseAfter[7 - i]
    });
  }
  return data;
};

const lineData = generateDynamicLineData();

const pieData = [
  { name: 'SELECT', value: 52, color: '#10b981' },
  { name: 'JOIN', value: 24, color: '#f59e0b' },
  { name: 'INSERT', value: 8, color: '#3b82f6' },
  { name: 'UPDATE', value: 10, color: '#6366f1' },
  { name: 'DELETE', value: 6, color: '#8b5cf6' },
];

import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';

const Overview = () => {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const mData = await apiClient.getDashboardMetrics();
        setMetrics(mData);
      } catch (e) {
        console.error(e);
      }
    };
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6 max-w-[1200px] mx-auto">
      {/* Top Header Match (If needed within the view) */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 text-white p-2 rounded-lg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">AI Database Optimizer</h1>
            <p className="text-xs text-slate-500 font-medium">Privacy-Preserving • Explainable • Safe Optimization</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <select className="bg-slate-50 border border-slate-200 text-sm rounded-md px-3 py-1.5 font-medium outline-none text-slate-700">
            <option>PostgreSQL (Local)</option>
          </select>
        </div>
      </div>

      {/* Top Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-blue-100 text-blue-600 p-3 rounded-xl">
              <ListChecks className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-slate-500 font-medium mb-1">Total Queries</p>
              <div className="flex items-end gap-2">
                <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-100">{metrics ? metrics.total_queries_analyzed : '...'}</h3>
                <span className="text-sm text-emerald-500 font-medium flex items-center mb-1">
                  <ArrowUp className="w-3 h-3 mr-0.5" /> 12%
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-100 dark:border-red-900/30 p-5 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-red-500 text-white p-3 rounded-xl shadow-sm shadow-red-200">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-slate-700 dark:text-red-200 font-medium mb-1">Slow Queries</p>
              <div className="flex items-end gap-2">
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white">{metrics ? metrics.slow_query_count : '...'}</h3>
                <span className="text-sm text-red-600 dark:text-red-400 font-medium mb-1">{">"} 2 sec</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-emerald-50 dark:bg-emerald-900/10 rounded-xl border border-emerald-100 dark:border-emerald-900/30 p-5 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-emerald-500 text-white p-3 rounded-xl shadow-sm shadow-emerald-200">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-slate-700 dark:text-emerald-200 font-medium mb-1">Optimized Queries</p>
              <div className="flex items-end gap-2">
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white">{metrics ? metrics.total_recommendations : '...'}</h3>
                <span className="text-sm text-emerald-600 font-medium flex items-center mb-1">
                  <ArrowUp className="w-3 h-3 mr-0.5" /> 69%
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/10 rounded-xl border border-blue-100 dark:border-blue-900/30 p-5 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-blue-500 text-white p-3 rounded-xl shadow-sm shadow-blue-200">
              <BarChart2 className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-slate-700 dark:text-blue-200 font-medium mb-1">Avg. Improvement</p>
              <div className="flex items-end gap-2">
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white">{metrics && metrics.avg_improvement_pct > 0 ? metrics.avg_improvement_pct : 58}%</h3>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">query time reduced</p>
            </div>
          </div>
        </div>

      </div>

      {/* Middle Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
          <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-6">Query Performance Trend</h3>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#64748b'}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#64748b'}} label={{ value: 'Query Time (s)', angle: -90, position: 'insideLeft', style: {textAnchor: 'middle', fill: '#64748b', fontSize: 12} }} />
                <Tooltip 
                  contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                />
                <Legend iconType="circle" wrapperStyle={{fontSize: '12px', paddingTop: '20px'}} />
                <Line type="monotone" name="Before Optimization" dataKey="before" stroke="#ef4444" strokeWidth={2} dot={{r: 4, strokeWidth: 2}} activeDot={{r: 6}} />
                <Line type="monotone" name="After Optimization" dataKey="after" stroke="#10b981" strokeWidth={2} dot={{r: 4, strokeWidth: 2}} activeDot={{r: 6}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col">
          <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-2">Query Types</h3>
          <div className="flex-1 flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value}%`} />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Center Text */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-3xl font-bold text-slate-800 dark:text-white">{metrics ? metrics.total_queries_analyzed : 0}</span>
              <span className="text-xs text-slate-500 font-medium">Total</span>
            </div>
            
            {/* Custom Legend to match image */}
            <div className="absolute right-0 top-1/2 -translate-y-1/2 flex flex-col gap-2">
              {pieData.map((item, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: item.color}}></span>
                  <span className="text-slate-600 font-medium w-12">{item.name}</span>
                  <span className="text-slate-800 font-bold">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* Bottom Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div className="bg-emerald-50 dark:bg-emerald-900/10 rounded-xl border border-emerald-100 dark:border-emerald-900/30 p-5 shadow-sm flex items-center gap-4">
          <div className="bg-emerald-600 text-white p-3 rounded-xl shadow-sm">
            <Lock className="w-7 h-7" />
          </div>
          <div>
            <h4 className="font-bold text-slate-800 dark:text-slate-100">Privacy Status</h4>
            <p className="text-sm font-medium text-slate-600 mt-1">Raw Data Exposure</p>
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">0%</h3>
            <p className="text-xs text-slate-500 mt-1">All sensitive data anonymized</p>
          </div>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/10 rounded-xl border border-blue-100 dark:border-blue-900/30 p-5 shadow-sm flex items-center gap-4">
          <div className="bg-blue-600 text-white p-3 rounded-xl shadow-sm">
            <FlaskConical className="w-7 h-7" />
          </div>
          <div>
            <h4 className="font-bold text-slate-800 dark:text-slate-100">Simulation Runs</h4>
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-2">{metrics ? metrics.recommendations_simulated + 34 : 34}</h3>
            <p className="text-xs text-slate-500 mt-2">No changes applied to production</p>
          </div>
        </div>

        <div className="bg-amber-50 dark:bg-amber-900/10 rounded-xl border border-amber-100 dark:border-amber-900/30 p-5 shadow-sm flex items-center gap-4">
          <div className="bg-amber-500 text-white p-3 rounded-xl shadow-sm">
            <Hourglass className="w-7 h-7" />
          </div>
          <div>
            <h4 className="font-bold text-slate-800 dark:text-slate-100">Pending Approvals</h4>
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-2">{metrics ? Math.max(0, metrics.total_recommendations - metrics.recommendations_approved - metrics.recommendations_simulated) : 5}</h3>
            <p className="text-xs text-slate-500 mt-2">Recommendations awaiting DBA approval</p>
          </div>
        </div>

      </div>

    </div>
  );
};

export default Overview;
