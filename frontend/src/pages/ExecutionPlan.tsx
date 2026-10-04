import React, { useState } from 'react';
import { GitBranch, ChevronRight, ChevronDown, Clock, Database, AlertCircle, Lightbulb, ExternalLink } from 'lucide-react';
import { apiClient } from '../api/client';

const ExecutionPlan = () => {
  const [inputMode, setInputMode] = useState<'sql' | 'json'>('sql');
  const [sql, setSql] = useState('');
  const [planJson, setPlanJson] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('graph');
  const [selectedNode, setSelectedNode] = useState<any>(null);

  const handleGenerateAndAnalyze = async () => {
    try {
      setAnalyzing(true);
      setError(null);
      let parsed;
      
      if (inputMode === 'sql') {
        const res = await apiClient.generatePlan(sql);
        if (res.error) throw new Error(res.error);
        parsed = res.plan_json;
        setPlanJson(JSON.stringify(parsed, null, 2));
      } else {
        try {
          parsed = JSON.parse(planJson);
        } catch(e) {
          throw new Error("Invalid JSON format.");
        }
      }
      
      const data = await apiClient.analyzePlan(parsed);
      setResult(data);
      if (data && data.execution_tree) {
        setSelectedNode(data.execution_tree);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const loadDemo = () => {
    setPlanJson(JSON.stringify([{
      "Plan": {
        "Node Type": "Hash Join",
        "Total Cost": 420532,
        "Actual Rows": 1250000,
        "status": "bottleneck",
        "Plans": [
          {
            "Node Type": "Seq Scan",
            "Relation Name": "orders",
            "Total Cost": 310215,
            "Actual Rows": 1200000,
            "status": "bottleneck",
            "Plans": [
              {
                "Node Type": "Filter",
                "Filter": "order_date >= '2026-01-01'",
                "Actual Rows": 800000,
                "status": "warning"
              }
            ]
          },
          {
            "Node Type": "Index Scan",
            "Relation Name": "customers",
            "Total Cost": 10320,
            "Actual Rows": 100000,
            "status": "healthy"
          }
        ]
      }
    }], null, 2));
  };

  const getNodeColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 border-green-500 text-green-900';
      case 'warning': return 'bg-yellow-100 border-yellow-500 text-yellow-900';
      case 'critical':
      case 'bottleneck': return 'bg-red-100 border-red-500 text-red-900 shadow-red-200';
      default: return 'bg-slate-50 border-slate-300 text-slate-800';
    }
  };

  // Simplified Recursive json Component (Mocking the visual json structure)
  const renderTree = (node: any, level = 0) => {
    if (!node) return null;
    const isSelected = selectedNode === node;
    
    return (
      <div key={Math.random()} className="flex flex-col items-center">
        <div 
          onClick={() => setSelectedNode(node)}
          className={`px-6 py-3 rounded-xl border-2 text-center min-w-[200px] cursor-pointer shadow-sm transition-all ${getNodeColor(node.status || 'healthy')} ${isSelected ? 'ring-2 ring-blue-500 shadow-md' : 'hover:shadow-md'}`}
        >
          <p className="font-bold text-slate-800">{node.node_type || node["Node Type"]}</p>
          {(node.relation_name || node["Relation Name"]) && <p className="text-sm font-medium text-slate-700">{node.relation_name || node["Relation Name"]}</p>}
                    <p className="text-xs text-slate-600 mt-1">(cost: {(node.cost || node["Total Cost"] || 0).toLocaleString()})</p>
                    <p className="text-xs text-slate-600">(rows: {(node.rows ?? node["Actual Rows"] ?? node["Plan Rows"] ?? 0).toLocaleString()})</p>
        </div>
        
        {((node.children && node.children.length > 0) || (node.Plans && node.Plans.length > 0)) && (
          <div className="flex flex-col items-center mt-2">
            <div className="w-px h-6 bg-slate-400"></div>
            <div className="flex justify-center relative">
              <div className="flex gap-8">
                {(node.children || node.Plans).map((child: any) => (
                  <div key={Math.random()} className="flex flex-col items-center">
                    <div className="w-px h-6 bg-slate-400"></div>
                    {renderTree(child, level + 1)}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold flex items-center text-slate-800 dark:text-slate-100">
            3. Execution Plan (GNN-based Visualization)
          </h2>
        </div>
        <button onClick={loadDemo} className="text-sm text-blue-600 hover:underline">Load Demo JSON</button>
      </div>

      {/* Top Bar */}
      <div className="flex justify-between items-center bg-white dark:bg-slate-900 p-2 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex space-x-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg">
          <button 
            className={`px-6 py-2 rounded-md text-sm font-bold ${activeTab === 'graph' ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:bg-slate-200'}`}
            onClick={() => setActiveTab('graph')}
          >
            Graph View
          </button>
          <button 
            className={`px-6 py-2 rounded-md text-sm font-bold ${activeTab === 'json' ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:bg-slate-200'}`}
            onClick={() => setActiveTab('json')}
          >
            Raw JSON
          </button>
        </div>
        <button className="flex items-center px-4 py-2 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg font-medium text-sm">
          <ExternalLink className="w-4 h-4 mr-2" /> Explain Plan
        </button>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left: Visual json */}
        <div className="w-full lg:w-2/3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm overflow-x-auto min-h-[500px]">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-bold text-slate-800 dark:text-slate-100 flex items-center">
              <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded mr-2 font-mono border border-purple-200">LIVE DB CONNECTION</span>
              Query Execution Plan (GNN Graph)
            </h3>
          </div>
          <p className="text-sm text-slate-500 mb-4 bg-slate-50 p-3 rounded-lg border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
            When you click Generate, our backend connects directly to PostgreSQL via psycopg2, runs <code>EXPLAIN (FORMAT JSON)</code>, and parses the output into a Graph Neural Network (GCN) layer to mathematically detect bottlenecks.
          </p>
          
          {!result ? (
            <div className="flex flex-col items-center justify-center h-[400px] text-slate-400 border-2 border-dashed border-slate-200 rounded-xl p-8">
              <div className="flex space-x-2 mb-4 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
                <button 
                  onClick={() => setInputMode('sql')} 
                  className={`px-4 py-1.5 rounded-md text-sm font-medium ${inputMode === 'sql' ? 'bg-white shadow text-slate-800' : 'text-slate-500'}`}
                >SQL Query</button>
                <button 
                  onClick={() => setInputMode('json')} 
                  className={`px-4 py-1.5 rounded-md text-sm font-medium ${inputMode === 'json' ? 'bg-white shadow text-slate-800' : 'text-slate-500'}`}
                >JSON Plan</button>
              </div>
              
              {inputMode === 'sql' ? (
                <textarea
                  value={sql}
                  onChange={(e) => setSql(e.target.value)}
                  placeholder="Paste your raw SQL query here... (We will run EXPLAIN for you)"
                  defaultValue="SELECT c.name, sum(o.total_amount)
FROM customers c 
JOIN orders o ON c.id = o.customer_id 
WHERE c.region_id = 5 
GROUP BY c.name 
ORDER BY sum(o.total_amount) DESC;"
                  className="w-full max-w-lg h-32 p-4 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-mono mb-4 resize-none"
                />
              ) : (
                <textarea
                  value={planJson}
                  onChange={(e) => setPlanJson(e.target.value)}
                  placeholder="Paste PostgreSQL EXPLAIN (FORMAT JSON) array here..."
                  className="w-full max-w-lg h-32 p-4 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-mono mb-4 resize-none"
                />
              )}
              
              <button 
                onClick={handleGenerateAndAnalyze}
                disabled={(inputMode === 'sql' ? !sql : !planJson) || analyzing}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-bold disabled:opacity-50"
              >
                {analyzing ? 'Analyzing...' : 'Generate Graph'}
              </button>
              {error && <p className="text-red-500 mt-2 text-sm max-w-md text-center">{error}</p>}
            </div>
          ) : activeTab === 'graph' ? (
            <div className="flex justify-center pt-8 overflow-auto">
              {renderTree(result.execution_tree || JSON.parse(planJson)[0].Plan)}
            </div>
        ) : (
            <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg overflow-auto max-h-[600px] text-xs font-mono">
              <pre>{JSON.stringify(result.execution_tree || JSON.parse(planJson)[0].Plan, null, 2)}</pre>
            </div>
        )}
        </div>

        {/* Right: Node Details */}
        <div className="w-full lg:w-1/3 flex flex-col space-y-6">
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
            <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-4 border-b border-slate-100 pb-2">Node Details</h3>
            
            {selectedNode ? (
              <div className="space-y-3 text-sm">
                <div className="flex justify-between border-b border-slate-50 pb-2">
                  <span className="text-slate-500">Node Type</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{selectedNode.node_type || selectedNode["Node Type"]}</span>
                </div>
                <div className="flex justify-between border-b border-slate-50 pb-2">
                  <span className="text-slate-500">Table</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{selectedNode.relation_name || selectedNode["Relation Name"] || '-'}</span>
                </div>
                <div className="flex justify-between border-b border-slate-50 pb-2">
                  <span className="text-slate-500">Estimated Rows</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{(selectedNode.rows || selectedNode["Actual Rows"] || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between border-b border-slate-50 pb-2">
                  <span className="text-slate-500">Actual Rows</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{(selectedNode.rows || selectedNode["Actual Rows"] || 0).toLocaleString()}</span>
                </div>
                                  <div className="flex justify-between border-b border-slate-50 pb-2">
                    <span className="text-slate-500">Cumulative Cost</span>
                    <span className="font-medium text-slate-800 dark:text-slate-200">{(selectedNode.cost || selectedNode["Total Cost"] || 0).toLocaleString()}</span>
                  </div>
                <div className="flex justify-between border-b border-slate-50 pb-2">
                  <span className="text-slate-500">Condition</span>
                  <span className="font-medium text-slate-800 dark:text-slate-200">{selectedNode.Filter || '-'}</span>
                </div>
                <div className="flex justify-between pt-1">
                  <span className="text-slate-500">Issue</span>
                  <span className={`font-bold ${selectedNode.status === 'bottleneck' ? 'text-red-500' : 'text-slate-400'}`}>
                    {selectedNode.status === 'bottleneck' ? 'High cost due to full table scan or inefficient join' : 'None'}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-slate-400 text-sm text-center py-8">Select a node in the graph to view details</p>
            )}
          </div>

          <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-200 dark:border-purple-800/50 p-6 shadow-sm flex items-start">
            <div className="bg-purple-600 rounded-full p-2 mr-4 text-white flex-shrink-0">
              <Lightbulb className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-2">GNN Analysis Result</h3>
              <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                  {selectedNode ? (
                    selectedNode.status === 'bottleneck' ? (
                      `The GNN model identifies this ${selectedNode.node_type || selectedNode["Node Type"]} on ${selectedNode.relation_name || selectedNode["Relation Name"] || 'the table'} as a major bottleneck, requiring attention. It contributes heavily to the total query cost of ${(selectedNode.cost || selectedNode["Total Cost"] || 0).toLocaleString()}.`
                    ) : selectedNode.status === 'warning' ? (
                      `The GNN model flags this ${selectedNode.node_type || selectedNode["Node Type"]} as slightly inefficient but not critical. Cost: ${(selectedNode.cost || selectedNode["Total Cost"] || 0).toLocaleString()}.`
                    ) : (
                      `The GNN model analyzes this ${selectedNode.node_type || selectedNode["Node Type"]} as healthy. Execution cost is optimal.`
                    )
                  ) : (
                    "Select a node in the graph to view its GNN analysis."
                  )}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutionPlan;







