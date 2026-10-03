import React from 'react';

const MetricCard = ({ title, value, icon, change }: any) => (
  <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex items-center justify-between">
    <div>
      <p className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">{title}</p>
      <div className="flex items-baseline space-x-2">
        <h4 className="text-3xl font-bold">{value}</h4>
        <span className="text-xs font-medium text-green-600 dark:text-green-400">{change}</span>
      </div>
    </div>
    <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
      {icon}
    </div>
  </div>
);

export default MetricCard;
