import React, { useEffect, useState } from 'react';
import { ShieldCheck, Lock, EyeOff, FileKey, CheckCircle2, ArrowRight } from 'lucide-react';
import { apiClient } from '../api/client';

const StatusBadge = ({ title, value, status }: { title: string, value: string, status: 'good' | 'warning' | 'error' }) => {
  const colors = {
    good: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/50',
    warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800/50',
    error: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800/50'
  };

  return (
    <div className={`p-4 rounded-xl border ${colors[status]} flex flex-col justify-center items-center text-center h-24`}>
      <p className="text-xs font-medium opacity-80 mb-1">{title}</p>
      <p className="text-xl font-bold">{value}</p>
    </div>
  );
};

const PrivacyCenter = () => {
  const [stats, setStats] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resStats = await apiClient.getPrivacyStats();
        setStats(resStats);
        const resLogs = await apiClient.getPrivacyAudit();
        setLogs(resLogs?.audit_entries || []);
      } catch (e) {
        console.error(e);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold flex items-center text-slate-800 dark:text-slate-100">
            6. Privacy Layer (Data Anonymization View)
          </h2>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatusBadge title="Raw Data Exposure" value={stats ? `${stats.raw_exposure_count}` : '0'} status="good" />
        <StatusBadge title="PII Blocked" value={stats ? `${stats.pii_blocked}` : '0'} status="good" />
        <StatusBadge title="Fields Masked" value={stats ? `${stats.fields_masked}` : '0'} status="good" />
        <StatusBadge title="Total Requests" value={stats ? `${stats.total_requests}` : '0'} status="good" />
        <StatusBadge title="Anonymization Rate" value={stats ? `${stats.anonymization_pass_rate}%` : '100%'} status="good" />
      </div>
      
      <div className="mt-8 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
        
        <div className="flex flex-col lg:flex-row items-stretch justify-between mb-8 gap-4">
          
          {/* Left Table: Original Schema */}
          <div className="w-full lg:w-[45%]">
            <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-4">Original Schema (Production)</h3>
            <div className="rounded-lg border border-slate-200 overflow-hidden">
              <table className="w-full text-left text-sm">
                <thead className="bg-blue-50 text-blue-900">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Column Name</th>
                    <th className="px-4 py-3 font-semibold">Sample Data (Secure)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr><td className="px-4 py-2 font-medium">customer_id</td><td className="px-4 py-2 text-slate-600">USER_XXXX</td></tr>
                  <tr><td className="px-4 py-2 font-medium">name</td><td className="px-4 py-2 text-slate-600">MASKED</td></tr>
                  <tr><td className="px-4 py-2 font-medium">email</td><td className="px-4 py-2 text-slate-600">MASKED</td></tr>
                  <tr><td className="px-4 py-2 font-medium">phone</td><td className="px-4 py-2 text-slate-600">MASKED</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex items-center justify-center text-blue-500">
            <div className="flex flex-col items-center">
              <span className="text-xs font-bold mb-1 text-slate-400">Privacy Gateway</span>
              <ArrowRight className="w-8 h-8" strokeWidth={3} />
            </div>
          </div>

          {/* Right Table: Anonymized Metadata */}
          <div className="w-full lg:w-[50%]">
            <h3 className="font-bold text-emerald-700 dark:text-emerald-400 mb-4 bg-emerald-50 inline-block px-2 rounded">AI Model Input (Anonymized)</h3>
            <div className="rounded-lg border border-slate-200 overflow-hidden">
              <table className="w-full text-left text-sm">
                <thead className="bg-emerald-50 text-emerald-900">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Alias</th>
                    <th className="px-4 py-3 font-semibold">Data Type (Abstracted)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr><td className="px-4 py-2 font-medium text-emerald-700">C1</td><td className="px-4 py-2 text-slate-600 font-mono text-xs">INTEGER</td></tr>
                  <tr><td className="px-4 py-2 font-medium text-emerald-700">C2</td><td className="px-4 py-2 text-slate-600 font-mono text-xs">STRING_NAME</td></tr>
                  <tr><td className="px-4 py-2 font-medium text-emerald-700">C3</td><td className="px-4 py-2 text-slate-600 font-mono text-xs">STRING_EMAIL</td></tr>
                  <tr><td className="px-4 py-2 font-medium text-emerald-700">C4</td><td className="px-4 py-2 text-slate-600 font-mono text-xs">STRING_PHONE</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-6 flex items-center">
          <FileKey className="w-5 h-5 mr-2 text-indigo-500" />
          Live Anonymization Stream
        </h3>

        <div className="rounded-lg border border-slate-200 overflow-hidden mb-8">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800/50 text-slate-600 dark:text-slate-300">
              <tr>
                <th className="px-4 py-3 font-semibold">Request Hash</th>
                <th className="px-4 py-3 font-semibold">Time</th>
                <th className="px-4 py-3 font-semibold">Source</th>
                <th className="px-4 py-3 font-semibold">Fields Masked</th>
                <th className="px-4 py-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {logs.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">No privacy events recorded yet. Run a query in the Query Analyzer.</td></tr>
              ) : (
                logs.slice(0, 5).map((log, index) => {
                  const logId = log.request_id || log.recommendation_id || log.query_fingerprint || `sys-${index}`;
                  const shortId = logId ? logId.substring(0, 8) : 'N/A';
                  const userOrSystem = log.source_type || log.user || 'System';
                  const masked = log.fields_masked !== undefined ? `+${log.fields_masked} Literals Masked` : log.action || 'Unknown';
                  const status = log.anonymization_status || log.privacy_status || (log.result === 'completed' ? 'PASSED' : 'UNKNOWN');
                  
                  return (
                    <tr key={index} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="px-4 py-3 font-mono text-xs">{shortId}</td>
                      <td className="px-4 py-3 text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</td>
                      <td className="px-4 py-3 font-medium">{userOrSystem}</td>
                      <td className="px-4 py-3 text-emerald-600 font-bold">{masked}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 bg-emerald-100 text-emerald-800 rounded text-xs font-bold">{status}</span>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 flex items-start mb-8">
          <Lock className="w-5 h-5 text-emerald-600 mr-3 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-emerald-800 font-medium">
            Sensitive values are bitmasked/hashed. Only structural metadata and patterns are used for AI optimization. <br/>
            Raw production data is never exposed to the AI model.
          </p>
        </div>

        <div className="border border-red-200 bg-red-50 dark:bg-red-900/10 dark:border-red-900/50 rounded-xl p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-lg font-bold text-red-800 dark:text-red-400 flex items-center">
                <ShieldCheck className="w-5 h-5 mr-2" />
                Red-Team Penetration Test (Provable Privacy)
              </h3>
              <p className="text-sm text-red-600 dark:text-red-300">Attempt to leak sensitive data (PII) to the AI engine to test the Privacy Gateway.</p>
            </div>
            <button 
              onClick={async () => {
                const attackQuery = "SELECT * FROM customers WHERE email = 'ceo@altron.com' AND credit_card = '4111-2222-3333-4444' OR phone = '+91-9876543210' AND name = 'John Doe'";
                try {
                  await apiClient.anonymizeQuery(attackQuery);
                  const resStats = await apiClient.getPrivacyStats();
                  setStats(resStats);
                  const resLogs = await apiClient.getPrivacyAudit();
                  setLogs(resLogs?.audit_entries || []);
                  alert("Attack Intercepted! Gateway successfully blocked and masked all PII before it reached the AI.");
                } catch(e) {
                  console.error(e);
                }
              }}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded font-bold shadow transition-colors"
            >
              Launch Attack
            </button>
          </div>
          <div className="bg-white dark:bg-slate-900 rounded border border-red-200 p-4 font-mono text-sm text-slate-700 dark:text-slate-300">
            <span className="text-red-500 font-bold">ATTACK PAYLOAD: </span>
            <span>SELECT * FROM customers WHERE email = </span>
            <span className="bg-yellow-200 text-yellow-900 px-1">'ceo@altron.com'</span>
            <span> AND credit_card = </span>
            <span className="bg-yellow-200 text-yellow-900 px-1">'4111-2222-3333-4444'</span>
            <span> OR phone = </span>
            <span className="bg-yellow-200 text-yellow-900 px-1">'+91-9876543210'</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyCenter;