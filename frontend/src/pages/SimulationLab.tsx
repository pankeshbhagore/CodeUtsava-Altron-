import React, { useEffect, useState } from 'react';
import { FlaskConical, Play, CheckCircle2, AlertTriangle, ArrowRight, ArrowRightCircle } from 'lucide-react';
import { apiClient } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const SimulationLab = () => {
  const [simulations, setSimulations] = useState<any[]>([]);
  const [selectedSimIdx, setSelectedSimIdx] = useState(0);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    const fetchSimulations = async () => {
      try {
        const res = await apiClient.getRecommendations();
        setSimulations(res?.simulations || []);
      } catch (e) {
        console.error(e);
      }
    };
    fetchSimulations();
  }, []);

  const currentSim = simulations[selectedSimIdx];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold flex items-center text-slate-800 dark:text-slate-100">
            5. Simulation (Before vs After Performance)
          </h2>
        </div>
      </div>

      {simulations.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-2">No Simulations Found</h3>
          <p className="text-slate-500 mb-6">Go to AI Recommendations and click "Run Simulation" to see before/after comparisons.</p>
          <button onClick={() => window.location.href='/recommendations'} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold">
            Go to Recommendations
          </button>
        </div>
      ) : (
        <div className="flex flex-col lg:flex-row gap-6">
          
          {/* Configuration Panel */}
          <div className="w-full lg:w-1/4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
            <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-2">Simulation Configuration</h3>
            <p className="text-xs text-slate-500 mb-6 leading-relaxed">
              Apply the recommended changes in an isolated test environment (simulatory environment using PostgreSQL).
            </p>
            
            <div className="space-y-4 mb-8">
              <label className="flex items-start">
                <input type="checkbox" defaultChecked className="mt-1 rounded text-blue-600 focus:ring-blue-500" />
                <span className="ml-3 text-sm text-slate-700 font-medium">Create proposed index</span>
              </label>
              <label className="flex items-start">
                <input type="checkbox" defaultChecked className="mt-1 rounded text-blue-600 focus:ring-blue-500" />
                <span className="ml-3 text-sm text-slate-700 font-medium">Run query with same parameters</span>
              </label>
              <label className="flex items-start">
                <input type="checkbox" defaultChecked className="mt-1 rounded text-blue-600 focus:ring-blue-500" />
                <span className="ml-3 text-sm text-slate-700 font-medium">Compare performance metrics</span>
              </label>
            </div>
            
            <button 
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-bold transition-colors shadow-sm"
              onClick={() => { setRunning(true); setTimeout(() => setRunning(false), 800) }}
            >
              {running ? 'Running...' : 'Run Simulation'}
            </button>
          </div>
          {/* Performance Comparison Panel */}
          <div className="w-full lg:w-2/4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col">
            <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-6">Performance Comparison</h3>
            
            <div className="h-48 w-full mb-6">
              <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={[
                    { name: 'Execution Time (ms)', Before: currentSim.before_metrics.execution_time_ms, After: currentSim.after_metrics.execution_time_ms }
                  ]} margin={{top: 10, right: 10, left: -20, bottom: 0}}>
                    <XAxis dataKey="name" stroke="#888" fontSize={12} />
                    <YAxis stroke="#888" fontSize={12} />
                    <Tooltip cursor={{fill: 'transparent'}} />
                    <Legend />
                    <Bar dataKey="Before" fill="#ef4444" radius={[4,4,0,0]} barSize={40} />
                    <Bar dataKey="After" fill="#10b981" radius={[4,4,0,0]} barSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="flex items-center justify-between">
              
              {/* Before */}
              <div className="w-[45%]">
                <div className="bg-red-50 text-red-700 py-2 px-4 rounded-t-lg font-bold text-sm text-center border-b border-red-100">
                  ?? Before Optimization
                </div>
                <div className="border border-slate-100 rounded-b-lg">
                  <div className="flex justify-between py-3 px-4 border-b border-slate-50 text-sm">
                    <span className="text-slate-500">Execution Time</span>
                    <span className="font-bold text-red-500">{currentSim.before_metrics.execution_time_ms.toFixed(2)} ms</span>
                  </div>
                  <div className="flex justify-between py-3 px-4 border-b border-slate-50 text-sm">
                    <span className="text-slate-500">Planning Time</span>
                    <span className="font-medium text-slate-700">45 ms</span>
                  </div>
                  <div className="flex justify-between py-3 px-4 border-b border-slate-50 text-sm">
                    <span className="text-slate-500">CPU Cost</span>
                    <span className="font-medium text-slate-700">{Math.round(currentSim.before_metrics.cpu_cost)}</span>
                  </div>
                  <div className="flex justify-between py-3 px-4 border-b border-slate-50 text-sm">
                    <span className="text-slate-500">Storage Usage</span>
                    <span className="font-medium text-slate-700">{currentSim.before_metrics.storage_mb} MB</span>
                  </div>
                  <div className="flex justify-between py-3 px-4 text-sm">
                    <span className="text-slate-500">Write Latency</span>
                    <span className="font-medium text-slate-700">{currentSim.before_metrics.write_latency_ms} ms</span>
                  </div>
                </div>
              </div>

              {/* Arrow */}
              <div className="text-slate-300">
                <ArrowRightCircle className="w-6 h-6" />
              </div>

              {/* After */}
              <div className="w-[45%]">
                <div className="bg-emerald-50 text-emerald-800 py-2 px-4 rounded-t-lg font-bold text-sm text-center border-b border-emerald-100 flex justify-center items-center">
                  <CheckCircle2 className="w-4 h-4 mr-2" /> After Optimization (Simulated)
                </div>
                <div className="border border-slate-100 rounded-b-lg">
                  <div className="flex justify-between py-3 px-4 border-b border-slate-50 text-sm">
                    <span className="text-slate-500">Execution Time</span>
                    <span className="font-bold text-emerald-500">{currentSim.after_metrics.execution_time_ms.toFixed(2)} ms</span>
                  </div>
                  <div className="flex justify-between py-3 px-4 border-b border-slate-50 text-sm">
                    <span className="text-slate-500">Planning Time</span>
                    <span className="font-medium text-emerald-600">32 ms</span>
                  </div>
                  <div className="flex justify-between py-3 px-4 border-b border-slate-50 text-sm">
                    <span className="text-slate-500">CPU Cost</span>
                    <span className="font-medium text-emerald-600">{Math.round(currentSim.after_metrics.cpu_cost)}</span>
                  </div>
                  <div className="flex justify-between py-3 px-4 border-b border-slate-50 text-sm">
                    <span className="text-slate-500">Storage Usage</span>
                    <span className="font-medium text-emerald-600">
                      {currentSim.after_metrics.storage_mb} MB <span className="text-xs">({currentSim.after_metrics.storage_mb > currentSim.before_metrics.storage_mb ? '+' : ''}{currentSim.after_metrics.storage_mb - currentSim.before_metrics.storage_mb} MB)</span>
                    </span>
                  </div>
                  <div className="flex justify-between py-3 px-4 text-sm">
                    <span className="text-slate-500">Write Latency</span>
                    <span className="font-medium text-emerald-600">{currentSim.after_metrics.write_latency_ms} ms</span>
                  </div>
                </div>
              </div>

            </div>
          </div>

                      {/* Improvement Panel */}
            <div className="w-full lg:w-1/4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col items-center justify-between">
              <div className="w-full">
                <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-6 w-full text-left">Estimated Improvement</h3>
                
                <div className="relative w-40 h-40 flex items-center justify-center mx-auto">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="40" stroke="#f1f5f9" strokeWidth="12" fill="none" />
                    <circle 
                      cx="50" cy="50" r="40" 
                      stroke="#10b981" 
                      strokeWidth="12" 
                      fill="none" 
                      strokeDasharray="251.2" 
                      strokeDashoffset={251.2 - (251.2 * (simResult ? simResult.improvement_pct : 90) / 100)} 
                      strokeLinecap="round" 
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-3xl font-black text-slate-800 dark:text-slate-100">{simResult ? Math.round(simResult.improvement_pct) : 90}%</span>
                  </div>
                </div>
                <p className="text-emerald-600 font-bold mt-4 text-center">Query Time Reduced</p>
              </div>

              {simResult && simResult.before_metrics.carbon_emissions_grams !== undefined && (
                <div className="mt-8 w-full bg-emerald-50 dark:bg-emerald-900/20 p-4 rounded-xl border border-emerald-100 dark:border-emerald-800/30">
                  <h4 className="text-emerald-800 dark:text-emerald-400 font-bold text-sm mb-2 flex items-center">
                    ?? Green Computing Impact
                  </h4>
                  <p className="text-xs text-slate-600 dark:text-slate-300 mb-2">
                    Estimated CO2 reduction per 1M queries:
                  </p>
                  <div className="flex items-end space-x-2">
                    <span className="text-2xl font-black text-emerald-600">
                      {(simResult.before_metrics.carbon_emissions_grams - simResult.after_metrics.carbon_emissions_grams).toFixed(1)}
                    </span>
                    <span className="text-sm text-emerald-700 font-semibold mb-1">grams CO2</span>
                  </div>
                </div>
              )}
              
              <div className="mt-auto pt-8 w-full">
                <p className="text-xs text-slate-500 flex items-start">
                  <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0 text-emerald-500" />
                  Changes not applied to production. This is a simulated result.
                </p>
              </div>
            </div>

        </div>
      )}
    </div>
  );
};

export default SimulationLab;




