const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";
const TOKEN_STORAGE_KEY = "pybs_access_token";
const USER_STORAGE_KEY = "pybs_user";
const EXPIRES_STORAGE_KEY = "pybs_access_token_expires_at";

export function getStoredSession() {
  const token = window.localStorage.getItem(TOKEN_STORAGE_KEY);
  const user = window.localStorage.getItem(USER_STORAGE_KEY);
  const expiresAt = window.localStorage.getItem(EXPIRES_STORAGE_KEY);

  if (!token) {
    return null;
  }

  return {
    token,
    user: user ? JSON.parse(user) : null,
    expiresAt,
  };
}

export function persistSession(session) {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, session.token);
  window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(session.user));
  window.localStorage.setItem(EXPIRES_STORAGE_KEY, session.expiresAt || "");
}

export function clearStoredSession() {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  window.localStorage.removeItem(USER_STORAGE_KEY);
  window.localStorage.removeItem(EXPIRES_STORAGE_KEY);
}

async function request(path, options = {}) {
  const session = typeof window !== "undefined" ? getStoredSession() : null;
  const hasJsonBody = options.body && !(options.body instanceof FormData);
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      ...(hasJsonBody ? { "Content-Type": "application/json" } : {}),
      ...(session?.token ? { Authorization: `Bearer ${session.token}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `请求失败: ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || payload.message || message;
    } catch {
      // ignore json parsing error
    }

    if (response.status === 401 && typeof window !== "undefined") {
      clearStoredSession();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  if (options.rawResponse) {
    return response;
  }
  return response.json();
}

function buildQuery(params) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, value);
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : "";
}

export const api = {
  login(credentials) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  },
  getCurrentUser() {
    return request("/auth/me");
  },
  logout() {
    return request("/auth/logout", { method: "POST" });
  },
  getDashboard(days = 30) {
    return request(`/dashboard${buildQuery({ days })}`);
  },
  getRankings(limit = 5) {
    return request(`/dashboard/rankings${buildQuery({ limit })}`);
  },
  getSystemOptions() {
    return request("/system/options");
  },
  getTaskLogs(limit = 20) {
    return request(`/system/task-logs${buildQuery({ limit })}`);
  },
  getRawRecords(limit = 20) {
    return request(`/system/raw-records${buildQuery({ limit })}`);
  },
  getDataSources() {
    return request("/system/data-sources");
  },
  getReportAssets(limit = 10) {
    return request(`/system/report-assets${buildQuery({ limit })}`);
  },
  getThresholds() {
    return request("/system/thresholds");
  },
  updateThreshold(thresholdId, payload) {
    return request(`/system/thresholds/${thresholdId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },
  getPrices(filters = {}) {
    return request(`/prices${buildQuery(filters)}`);
  },
  async downloadPrices(filters = {}) {
    const response = await request(`/prices/export${buildQuery(filters)}`, {
      rawResponse: true,
      headers: {
        Accept: "text/csv",
      },
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "price-records.csv";
    document.body.append(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
  getAnalysisOverview(product, market) {
    return request(`/analysis/overview${buildQuery({ product, market })}`);
  },
  getAnalysisTrend(product, days = 90) {
    return request(`/analysis/trend${buildQuery({ product, days })}`);
  },
  getAnalysisMonthly(product, market) {
    return request(`/analysis/monthly${buildQuery({ product, market })}`);
  },
  getAnalysisRegions(product) {
    return request(`/analysis/regions${buildQuery({ product })}`);
  },
  getAnalysisVolatility(window_days = 30) {
    return request(`/analysis/volatility${buildQuery({ window_days })}`);
  },
  getAnalysisAnomalies(product, market, days = 120) {
    return request(`/analysis/anomalies${buildQuery({ product, market, days })}`);
  },
  getAlerts() {
    return request("/alerts");
  },
  getForecast(product = "大蒜", days = 30, model) {
    return request(`/alerts/forecast${buildQuery({ product, days, model })}`);
  },
};
