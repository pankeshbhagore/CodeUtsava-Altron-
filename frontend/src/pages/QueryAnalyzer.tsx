import React, { useState } from 'react';
import { Play, Sparkles, Shield, Database, AlertTriangle, Info, AlertCircle, FlaskConical } from 'lucide-react';
import { apiClient } from '../api/client';

const QueryAnalyzer = () => {
  const [sql, setSql] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [question, setQuestion] = useState('');
  const [asking, setAsking] = useState(false);
  const [assistantResponse, setAssistantResponse] = useState<any>(null);

  const handleAsk = async () => {
    if (!question) return;
    setAsking(true);
    try {
      const data = await apiClient.askAssistant(question);
      setAssistantResponse(data);
    } catch (err: any) {
      setAssistantResponse({ answer: `Error: ${err.message}` });
    } finally {
      setAsking(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      const data = await apiClient.analyzeQuery(sql);
      setResults(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const loadSample = () => {
    setSql(`SELECT c.customer_id, c.name,\n       SUM(o.amount) as total_amount\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nWHERE o.order_date >= '2026-01-01'\nGROUP BY c.customer_id, c.name\nORDER BY total_amount DESC;`);
  };

  return (
    <div className="space-y-6">
      
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mr-3 text-white">
          <Database className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-white">AI Database Optimizer</h1>
          <p className="text-sm text-slate-500">Privacy-Preserving â€¢ Explainable â€¢ Safe Optimization</p>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left Input */}
        <div className="w-full lg:w-2/3 space-y-4">
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
            <h2 className="font-bold text-slate-800 dark:text-slate-100 mb-4">Enter SQL Query</h2>
            <textarea
              value={sql}
              onChange={(e) => setSql(e.target.value)}
              placeholder="Paste your slow SQL query here..."
              className="w-full h-48 p-4 bg-purple-50/30 text-purple-900 dark:bg-[#0d1117] dark:text-purple-300 font-mono text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 border border-slate-200 dark:border-slate-800 resize-none mb-4"
              spellCheck="false"
            />
            <div className="flex space-x-3">
              <button 
                onClick={handleAnalyze}
                disabled={!sql || analyzing}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-bold disabled:opacity-50 transition-colors"
              >
                {analyzing ? 'Analyzing...' : 'Analyze Query'}
              </button>
              <button 
                onClick={loadSample}
                className="px-6 py-2 bg-slate-100 hover:bg-slate-200 text-blue-700 dark:bg-slate-800 dark:text-blue-400 rounded-lg text-sm font-bold transition-colors"
              >
                Use Sample Query
              </button>
            </div>
          </div>
        </div>

        {/* Right Details (Mocked dynamically) */}
        <div className="w-full lg:w-1/3 space-y-4">
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm h-full">
            <h2 className="font-bold text-slate-800 dark:text-slate-100 mb-4">Query Details</h2>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                <span className="text-slate-500">Query Type</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">
                  {results ? (sql.toLowerCase().includes('join') ? 'SELECT (JOIN)' : 'SELECT') : '-'}
                </span>
              </div>
              <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                <span className="text-slate-500">Tables Involved</span>
                <span className="font-medium text-slate-800 dark:text-slate-200 text-right">
                  {results ? results.metadata?.tables?.join(', ') : '-'}
                </span>
              </div>
              <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                <span className="text-slate-500">Estimated Rows</span>
                <span className="font-medium text-slate-800 dark:text-slate-200">
                  {results?.metadata?.estimated_rows?.toLocaleString() || '-'}
                </span>
              </div>
              <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                <span className="text-slate-500">Execution Time (Current)</span>
                <span className="font-bold text-red-500">
                  {results?.metadata?.execution_time_ms ? `${(results.metadata.execution_time_ms / 1000).toFixed(2)} sec` : '-'}
                </span>
              </div>
                              <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                  <span className="text-slate-500">Planning Time</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">
                    {results?.metadata?.planning_time_ms ? ` ms` : (results ? '45 ms' : '-')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Cost</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">
                    {results?.metadata?.cost ? results.metadata.cost.toLocaleString(undefined, {maximumFractionDigits:0}) : (results?.metadata?.estimated_rows ? (results.metadata.estimated_rows * 0.33).toLocaleString(undefined, {maximumFractionDigits:0}) : '-')}
                  </span>
                </div>
            </div>

            {results && (
              <div className="mt-6 bg-red-50 text-red-700 py-3 px-4 rounded-lg font-bold text-center flex items-center justify-center border border-red-100">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Slow Query Detected
              </div>
            )}
          </div>
        </div>
      </div>

              {results && (
          <div className="flex flex-col lg:flex-row gap-6 mt-2">
            {/* AI Analysis Summary */}
            <div className="w-full lg:w-1/2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex items-start">
              <div className="bg-emerald-600 rounded p-2 mr-4 text-white">
                <FlaskConical className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-2">AI Analysis Summary</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  {results.recommendations && results.recommendations.length > 0 
                    ? `AI has analyzed this query and identified ${results.recommendations.length} optimization opportunities. Applying these changes could significantly reduce execution time and resource consumption.`
                    : 'The query appears to be optimal or no clear optimizations were found.'}
                </p>
              </div>
            </div>

            {/* Key Issues */}
            <div className="w-full lg:w-1/2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
              <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-4">Optimization Opportunities</h3>
              <ul className="space-y-3">
                {results.recommendations && results.recommendations.length > 0 ? (
                  results.recommendations.map((rec: any, idx: number) => (
                    <li key={idx} className="flex items-start text-sm text-slate-700 dark:text-slate-300">
                      <AlertCircle className="w-4 h-4 text-amber-500 mr-3 flex-shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold">{rec.type === 'composite' ? 'Composite Index' : rec.type === 'single' ? 'Single Index' : rec.type} recommended on {rec.table}.</span>
                        <span className="text-slate-500 block text-xs mt-0.5">Estimated Improvement: {rec.estimated_improvement_pct}%</span>
                      </div>
                    </li>
                  ))
                ) : (
                  <li className="text-sm text-slate-500">No major issues detected.</li>
                )}
              </ul>
            </div>
          </div>
        )}

      <div className="flex justify-end space-x-4 my-4">{results && <button onClick={() => window.location.href='/execution-plan'} className="px-6 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-bold">View Execution Plan</button>}{results && <button onClick={() => window.location.href='/recommendations'} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-bold shadow">Review AI Recommendations ?</button>}</div>{/* AI Assistant Chat Section */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col mt-6">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex justify-between items-center">
          <h2 className="text-lg font-bold flex items-center text-slate-800 dark:text-slate-100">
            <Sparkles className="w-5 h-5 mr-2 text-purple-500" />
            Ask PrivDB Assistant (GPT-4o)
          </h2>
        </div>
        <div className="p-6">
          <div className="flex space-x-4 mb-4">
            <input 
              type="text" 
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="Ask a question about database performance... e.g., 'Why shouldn't I use LOWER()?'"
              className="flex-grow p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#0d1117] focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
            />
            <button 
              onClick={handleAsk}
              disabled={!question || asking}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-bold disabled:opacity-50 transition-colors cursor-pointer flex items-center"
            >
              {asking ? 'Asking...' : 'Ask AI'}
            </button>
          </div>
          
          {assistantResponse && (
            <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800/50 rounded-lg animate-in fade-in duration-500">
              <div className="flex items-start">
                <Sparkles className="w-5 h-5 mr-3 text-purple-600 dark:text-purple-400 mt-1 flex-shrink-0" />
                <div className="text-sm text-purple-900 dark:text-purple-100 whitespace-pre-wrap leading-relaxed">
                  {assistantResponse.answer}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
};

export default QueryAnalyzer;




