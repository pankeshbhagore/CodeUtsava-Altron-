import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import QueryAnalyzer from './pages/QueryAnalyzer';
import ExecutionPlan from './pages/ExecutionPlan';
import Recommendations from './pages/Recommendations';
import SimulationLab from './pages/SimulationLab';
import PrivacyCenter from './pages/PrivacyCenter';
import WorkloadDrift from './pages/WorkloadDrift';
import AuditLog from './pages/AuditLog';

function App() {
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  return (
    <Router>
      <Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode}>
        <Routes>
          <Route path="/" element={<Navigate to="/overview" replace />} />
          <Route path="/overview" element={<Overview />} />
          <Route path="/query-analyzer" element={<QueryAnalyzer />} />
          <Route path="/execution-plan" element={<ExecutionPlan />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/simulation-lab" element={<SimulationLab />} />
          <Route path="/privacy-center" element={<PrivacyCenter />} />
          <Route path="/workload-drift" element={<WorkloadDrift />} />
          <Route path="/audit-log" element={<AuditLog />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
