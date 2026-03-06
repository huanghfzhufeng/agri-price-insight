const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`请求失败: ${response.status}`);
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
  getDashboard(days = 30) {
    return request(`/dashboard${buildQuery({ days })}`);
  },
  getRankings(limit = 5) {
    return request(`/dashboard/rankings${buildQuery({ limit })}`);
  },
  getSystemOptions() {
    return request("/system/options");
  },
  getPrices(filters = {}) {
    return request(`/prices${buildQuery(filters)}`);
  },
  getAlerts() {
    return request("/alerts");
  },
  getForecast(product = "大蒜", days = 30) {
    return request(`/alerts/forecast${buildQuery({ product, days })}`);
  },
};
