import React from 'react';
import { Play, Download, ShieldAlert, ArrowRight, Check, X } from 'lucide-react';

const RecommendationCard = ({ rec }: any) => {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col md:flex-row gap-6">
      <div className="flex-1 space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <span className="inline-block px-2 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 text-xs font-semibold rounded mb-2">
              {rec.type}
            </span>
            <h3 className="text-lg font-bold">{rec.title}</h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">{rec.reason}</p>
          </div>
          <div className={`px-2 py-1 rounded text-xs font-semibold flex items-center ${
            rec.risk === 'Low' ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20' : 
            'bg-yellow-50 text-yellow-600 dark:bg-yellow-900/20'
          }`}>
            <ShieldAlert className="w-3 h-3 mr-1" />
            {rec.risk} Risk
          </div>
        </div>

        <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-lg border border-slate-200 dark:border-slate-800">
          <p className="text-xs font-semibold uppercase text-slate-500 mb-2">Evidence</p>
          <ul className="text-sm space-y-1 font-mono text-slate-700 dark:text-slate-300">
            {rec.evidence.map((e: string, i: number) => <li key={i}>• {e}</li>)}
          </ul>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-500">AI Confidence</span>
              <span className="font-semibold">{rec.confidence}%</span>
            </div>
            <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2">
              <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${rec.confidence}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      <div className="w-full md:w-64 flex flex-col justify-between border-t md:border-t-0 md:border-l border-slate-200 dark:border-slate-800 pt-6 md:pt-0 md:pl-6">
        <div className="space-y-3 mb-6">
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-500">Expected Speedup</span>
            <span className="text-emerald-500 font-bold flex items-center">{rec.improvement} <ArrowRight className="w-3 h-3 ml-1" /></span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-500">Storage Impact</span>
            <span className="text-slate-700 dark:text-slate-300 font-medium">{rec.storage}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-500">Write Latency</span>
            <span className="text-yellow-600 dark:text-yellow-400 font-medium">{rec.writeLatency}</span>
          </div>
        </div>

        <div className="space-y-2">
          <button className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center">
            <Play className="w-4 h-4 mr-2" /> Simulate
          </button>
          <div className="flex space-x-2">
            <button className="flex-1 py-2 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-900/20 dark:hover:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 rounded-lg text-sm font-medium transition-colors flex items-center justify-center border border-emerald-200 dark:border-emerald-800">
              <Check className="w-4 h-4 mr-1" /> Approve
            </button>
            <button className="flex-1 py-2 bg-slate-50 hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-medium transition-colors flex items-center justify-center border border-slate-200 dark:border-slate-700">
              <X className="w-4 h-4 mr-1" /> Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;
