import React, { useState, useEffect } from 'react';
import { History, Search, Filter } from 'lucide-react';
import { apiClient } from '../api/client';

const AuditLog = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await apiClient.getPrivacyAudit();
        setLogs(res?.audit_entries || []);
      } catch(e) {
        console.error(e);
      }
    };
    fetchLogs();
  }, []);

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold flex items-center">
            <History className="w-6 h-6 mr-2 text-slate-500" />
            Audit Log
          </h2>
          <p className="text-sm text-slate-500 mt-1">Track system events, approvals, and privacy actions</p>
        </div>
      </div>

      <div className="flex-1 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col">
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="relative w-full sm:w-96">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search logs by ID, user, or action..."
              className="w-full pl-9 pr-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="flex items-center px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg text-sm font-medium transition-colors">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </button>
        </div>
        <div className="flex-1 overflow-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 sticky top-0">
              <tr>
                <th className="px-6 py-4 font-medium">Log ID</th>
                <th className="px-6 py-4 font-medium">Timestamp</th>
                <th className="px-6 py-4 font-medium">User / System</th>
                <th className="px-6 py-4 font-medium">Action</th>
                <th className="px-6 py-4 font-medium">Target</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Privacy Assurance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">              {logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-500">No audit logs found.</td>
                </tr>
              ) : (
                logs.map((log, index) => {
                  const logId = log.request_id || log.recommendation_id || log.query_fingerprint || `sys-${index}`;
                  const shortId = logId ? logId.substring(0, 8) : 'N/A';
                  const userOrSystem = log.source_type || log.user || 'System';
                  const action = log.action || (log.fields_masked !== undefined ? `${log.fields_masked} Masked` : 'Unknown');
                  const target = log.ai_payload_hash ? log.ai_payload_hash.substring(0, 8) : (log.recommendation_id ? 'Recommendation' : 'Query');
                  const status = log.anonymization_status || log.privacy_status || (log.result === 'completed' ? 'PASSED' : 'UNKNOWN');
                  const privacyVerif = (log.raw_fields_detected === 0 || log.raw_data_exposed === 0) ? 'Verified' : 'Flagged';
                  
                  return (
                <tr key={index} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs">{shortId}</td>
                  <td className="px-6 py-4 text-slate-500">{new Date(log.timestamp).toLocaleString()}</td>
                  <td className="px-6 py-4 font-medium">{userOrSystem}</td>
                  <td className="px-6 py-4">{action}</td>
                  <td className="px-6 py-4 font-mono text-xs">{target}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      status === 'PASSED' || status === 'SUCCESS'
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' 
                      : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                    }`}>
                      {status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs font-medium text-blue-600 dark:text-blue-400 flex items-center">
                    {privacyVerif === 'Verified' && <span className="w-2 h-2 rounded-full bg-blue-500 mr-2"></span>}
                    {privacyVerif}
                  </td>
                </tr>
              )}))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AuditLog;

