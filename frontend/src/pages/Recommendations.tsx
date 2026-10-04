import React, { useEffect, useState } from 'react';
import { Brain, User, Calendar, FileCode, BarChart2, EyeOff, FileText, Lightbulb, Check, X, Play, Download, ShieldAlert, ArrowRight, Layers, Server, Settings, Copy, Clock, Database } from 'lucide-react';
import { apiClient } from '../api/client';

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [selectedRecId, setSelectedRecId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('index');

  useEffect(() => {
    const fetchRecs = async () => {
      try {
        const res = await apiClient.getRecommendations();
        const recs = res?.recommendations || [];
        setRecommendations(recs);
        if (recs.length > 0) {
          setSelectedRecId(recs[0].id);
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchRecs();
  }, []);

  const handleApprove = async (id: string) => {
    await apiClient.approveRecommendation(id);
    const res = await apiClient.getRecommendations();
    setRecommendations(res?.recommendations || []);
  };

  const handleSimulate = async (id: string) => {
    await apiClient.simulateRecommendation(id);
    window.location.href = '/simulation-lab';
  };

  const selectedRec = recommendations.find(r => r.id === selectedRecId);

  const tabs = [
    { id: 'index', label: 'Index Recommendations' },
    { id: 'rewrite', label: 'SQL Rewrite' },
    { id: 'partitioning', label: 'Partitioning / Sharding' },
    { id: 'config', label: 'Configuration' }
  ];

  return (
    <div className="space-y-4">
      {/* Top Tabs */}
      <div className="flex space-x-2 border-b border-slate-200 dark:border-slate-800 pb-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
              activeTab === tab.id 
                ? 'bg-blue-600 text-white' 
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex flex-col md:flex-row gap-6 h-[calc(100vh-200px)]">
        {/* Left Sidebar - List */}
        <div className="w-full md:w-1/3 flex flex-col space-y-3 overflow-y-auto pr-2">
          {recommendations.length === 0 ? (
            <div className="p-8 text-center text-slate-500 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm col-span-3">
              <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-2">No AI Recommendations Yet</h3>
              <p className="text-slate-500 mb-6">Analyze a query in the Query Analyzer to generate optimizations.</p>
              <button onClick={() => window.location.href='/query-analyzer'} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold">
                Go to Query Analyzer
              </button>
            </div>
          ) : (
            recommendations.map((rec, idx) => {
              const recType = (rec.type || 'Optimization').toLowerCase();
              let icon = <Brain className="w-4 h-4 text-emerald-600" />;
              let iconBg = "bg-emerald-100";
              let title = rec.type || 'Optimization';
              
              if (recType.includes('join') || recType.includes('single')) {
                icon = <User className="w-4 h-4 text-amber-600" />;
                iconBg = "bg-amber-100";
                title = "Optimize JOIN";
              } else if (recType.includes('partition')) {
                icon = <Calendar className="w-4 h-4 text-red-600" />;
                iconBg = "bg-red-100";
                title = "Partition by Date";
              } else if (recType.includes('rewrite') || recType.includes('sql')) {
                icon = <FileCode className="w-4 h-4 text-purple-600" />;
                iconBg = "bg-purple-100";
                title = "Query Rewrite";
              } else if (recType.includes('stats') || recType.includes('sharding')) {
                icon = <BarChart2 className="w-4 h-4 text-amber-500" />;
                iconBg = "bg-amber-50";
                title = "Statistics Update";
              } else if (recType.includes('composite')) {
                icon = <Brain className="w-4 h-4 text-emerald-600" />;
                iconBg = "bg-emerald-100";
                title = "Composite Index (Recommended)";
              }

              return (
                <div 
                  key={rec.id}
                  onClick={() => setSelectedRecId(rec.id)}
                  className={`p-3 rounded-lg border cursor-pointer flex items-center transition-all ${
                    selectedRecId === rec.id 
                      ? 'bg-emerald-50 border-emerald-300 text-emerald-900 shadow-sm' 
                      : 'bg-white border-slate-200 text-slate-700 hover:border-blue-300'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-md flex items-center justify-center mr-3 ${iconBg}`}>
                    {icon}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{idx + 1}. {title}</p>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Content - Details */}
        {selectedRec ? (
          <div className="w-full md:w-2/3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 flex flex-col shadow-sm overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 mb-1">Details</h2>
                <p className="text-slate-600 dark:text-slate-400 text-sm">{selectedRec.description}</p>
              </div>
              <span className="px-3 py-1 bg-emerald-600 text-white rounded text-xs font-semibold uppercase tracking-wider">
                High Impact
              </span>
            </div>

            {selectedRec.create_sql && (
              <div className="relative mb-6">
                <div className="bg-slate-50 dark:bg-[#0d1117] rounded-lg p-4 font-mono text-sm border border-slate-200 dark:border-slate-800 overflow-x-auto text-indigo-700 dark:text-indigo-300">
                  <pre>{selectedRec.create_sql}</pre>
                </div>
                <button className="absolute top-3 right-3 text-slate-400 hover:text-slate-600">
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            )}

            <div className="mb-6">
              <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-3">Why this helps?</h3>
              <ul className="list-disc pl-5 space-y-2 text-slate-600 dark:text-slate-300 text-sm">
                <li>{selectedRec.evidence || 'Both columns are frequently used in JOIN and WHERE clauses.'}</li>
                <li>Will reduce sequential scan cost on orders table.</li>
                <li>Improves join performance and overall query latency.</li>
              </ul>
            </div>
            
            <div className="mb-6 bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
              <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-2 flex items-center text-sm">
                <EyeOff className="w-4 h-4 mr-2 text-indigo-500" />
                Data Provided to AI (Zero Trust Masking)
              </h3>
              <p className="text-xs text-slate-500 mb-2">The AI model only saw this structurally masked query to preserve privacy:</p>
              <div className="bg-slate-900 rounded p-2 text-xs font-mono text-emerald-400 overflow-x-auto mb-2">
                {selectedRec.source_sql || "SELECT COL_1 FROM TABLE_1 WHERE COL_2 = ?"}
              </div>
              <p className="text-xs text-slate-500">Metadata sent: Estimated Rows: {selectedRec.metadata?.estimated_rows || 0}, Filters: {(selectedRec.metadata?.filter_columns || []).join(', ') || 'None'}</p>
            </div>

            <div>
              <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-3">Expected Impact</h3>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-3 border border-emerald-200 rounded-lg flex flex-col justify-center bg-emerald-50 dark:bg-emerald-900/20">
                  <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 flex items-center font-medium"><Clock className="w-4 h-4 mr-2 text-emerald-600"/> Query Time</p>
                  <p className="font-bold text-emerald-700 dark:text-emerald-400">8.24 s → {(8.24 * (1 - (selectedRec.estimated_improvement_pct || 62)/100)).toFixed(2)} s</p>
                  <p className="text-xs text-emerald-600 mt-0.5 font-medium flex items-center">↓ {selectedRec.estimated_improvement_pct || 62}%</p>
                </div>
                <div className="p-3 border border-slate-200 dark:border-slate-700 rounded-lg flex flex-col justify-center">
                  <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 flex items-center font-medium"><Database className="w-4 h-4 mr-2 text-purple-600"/> Storage Overhead</p>
                  <p className="font-bold text-slate-800 dark:text-slate-200">+{selectedRec.storage_overhead_mb || 120} MB</p>
                  <p className="text-xs text-slate-500 mt-0.5">(Estimated)</p>
                </div>
                <div className="p-3 border border-slate-200 dark:border-slate-700 rounded-lg flex flex-col justify-center">
                  <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 flex items-center font-medium"><BarChart2 className="w-4 h-4 mr-2 text-blue-500"/> Write Latency</p>
                  <p className="font-bold text-slate-800 dark:text-slate-200">+{selectedRec.write_latency_impact_ms || 2} ms</p>
                  <p className="text-xs text-slate-500 mt-0.5">(Estimated)</p>
                </div>
                <div className="p-3 border border-slate-200 dark:border-slate-700 rounded-lg flex flex-col justify-center">
                  <p className="text-xs text-slate-600 dark:text-slate-400 mb-1 flex items-center font-medium"><ShieldAlert className="w-4 h-4 mr-2 text-blue-600"/> Confidence Score</p>
                  <p className="font-bold text-slate-800 dark:text-slate-200 text-xl">{Math.round((selectedRec.confidence || 0.91) * 100)}%</p>
                </div>
              </div>
            </div>

                          <div className="mt-auto pt-6 flex space-x-3">
                {selectedRec.status === 'pending' && (
                  <button 
                    onClick={() => handleSimulate(selectedRec.id)}
                    className="px-6 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                  >
                    <Play className="w-4 h-4 mr-2" /> Run Simulation
                  </button>
                )}
                {selectedRec.status !== 'approved' && (
                  <button 
                    onClick={() => handleApprove(selectedRec.id)}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                  >
                    <Check className="w-4 h-4 mr-2" /> Approve & Apply
                  </button>
                )}
                <button 
                  onClick={async () => {
                    const res = await fetch('http://localhost:8000/api/recommendations/' + selectedRec.id + '/export-gitops');
                    const data = await res.json();
                    alert("GitOps Export Generated (Flyway & Liquibase)!\n\nFlyway Up: " + data.flyway.up_filename + "\n\n" + data.flyway.up_content);
                  }}
                  className="px-6 py-2 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-sm font-medium transition-colors flex items-center"
                >
                  Export GitOps
                </button>
              </div>
          </div>
        ) : (
          <div className="w-full md:w-2/3 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-800 flex items-center justify-center">
            <p className="text-slate-400">Select a recommendation to view details.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations;

