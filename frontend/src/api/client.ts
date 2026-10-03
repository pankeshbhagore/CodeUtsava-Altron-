const API_BASE_URL = 'http://localhost:8000/api';

async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json();
}

export const apiClient = {
  analyzeQuery: async (sql: string, executionStats?: any) => {
    return fetchAPI('/query/analyze', {
      method: 'POST',
      body: JSON.stringify({ sql, execution_stats: executionStats }),
    });
  },
  normalizeQuery: async (sql: string) => {
    return fetchAPI('/query/normalize', {
      method: 'POST',
      body: JSON.stringify({ sql }),
    });
  },
  anonymizeQuery: async (sql: string) => {
    return fetchAPI('/privacy/anonymize', {
      method: 'POST',
      body: JSON.stringify({ sql }),
    });
  },
  analyzePlan: async (plan: any) => {
    return fetchAPI('/plan/analyze', {
      method: 'POST',
      body: JSON.stringify({ plan_json: plan }),
    });
  },
  generatePlan: async (sql: string) => {
    return fetchAPI('/plan/generate', {
      method: 'POST',
      body: JSON.stringify({ sql }),
    });
  },
  generateRecommendations: async (sql: string, executionStats?: any, tableStats?: any) => {
    return fetchAPI('/recommendations/generate', {
      method: 'POST',
      body: JSON.stringify({ sql, execution_stats: executionStats, table_stats: tableStats }),
    });
  },
  simulateRecommendation: async (id: string) => {
    return fetchAPI(`/recommendations/${id}/simulate`, { method: 'POST' });
  },
  approveRecommendation: async (id: string) => {
    return fetchAPI(`/recommendations/${id}/approve`, { method: 'POST' });
  },
  rejectRecommendation: async (id: string) => {
    return fetchAPI(`/recommendations/${id}/reject`, { method: 'POST' });
  },
  getRecommendations: async () => {
    return fetchAPI('/recommendations/');
  },
    getRecentQueries: async () => {
    return fetchAPI('/dashboard/recent-queries');
  },
  getDashboardMetrics: async () => {
    return fetchAPI('/dashboard/metrics');
  },
  getPrivacyAudit: async () => {
    return fetchAPI('/privacy/audit');
  },
  getPrivacyStats: async () => {
    return fetchAPI('/privacy/stats');
  },
  getWorkloadDrift: async () => {
    return fetchAPI('/workload/drift');
  },
  getDemoSlowQueries: async () => {
    return fetchAPI('/demo/slow-queries');
  },
  getDemoExplainPlans: async () => {
    return fetchAPI('/demo/explain-plans');
  },
  analyzeAllDemo: async () => {
    return fetchAPI('/demo/analyze-all', { method: 'POST' });
  },
  askAssistant: async (question: string) => {
    return fetchAPI('/assistant/ask', {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  },
  resetDemo: async () => {
    return fetchAPI('/demo/reset', { method: 'POST' });
  }
};

