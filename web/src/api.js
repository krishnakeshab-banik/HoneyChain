const API = String(import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const TOKEN_KEY = "honeychain_token";
const REFRESH_KEY = "honeychain_refresh";
const QUEUE_KEY = "honeychain_offline_queue";

export function getToken() {
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function getRefreshToken() {
  return window.localStorage.getItem(REFRESH_KEY);
}

export function setRefreshToken(token) {
  if (token) {
    window.localStorage.setItem(REFRESH_KEY, token);
  }
}

export function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

export function storeAuthTokens(body) {
  if (body?.access_token) {
    setToken(body.access_token);
  }
  if (body?.refresh_token) {
    setRefreshToken(body.refresh_token);
  }
}

export function formatApiError(errorBody, status) {
  if (errorBody == null) {
    return `Couldn't complete that request (${status}).`;
  }
  const detail = errorBody.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item.loc) ? item.loc.slice(1).join(".") : "";
        return field ? `${field}: ${item.msg}` : item.msg || JSON.stringify(item);
      })
      .join(" ");
  }
  return `Couldn't complete that request (${status}).`;
}

async function parseBody(response) {
  if (response.status === 204) {
    return null;
  }
  const type = response.headers.get("content-type") || "";
  if (type.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

function readQueue() {
  try {
    return JSON.parse(window.localStorage.getItem(QUEUE_KEY) || "[]");
  } catch {
    return [];
  }
}

function writeQueue(items) {
  window.localStorage.setItem(QUEUE_KEY, JSON.stringify(items));
}

export async function flushOfflineQueue() {
  const items = readQueue();
  if (!items.length) {
    return;
  }
  const leftover = [];
  for (const item of items) {
    try {
      await apiRequest(item.method, item.path, item.payload, { skipQueue: true });
    } catch {
      leftover.push(item);
    }
  }
  writeQueue(leftover);
}

if (typeof window !== "undefined") {
  window.addEventListener("online", () => {
    flushOfflineQueue();
  });
}

let refreshInFlight = null;

async function refreshAccess() {
  const refresh = getRefreshToken();
  if (!refresh) {
    throw new Error("Your session expired. Sign in again.");
  }
  if (!refreshInFlight) {
    refreshInFlight = fetch(`${API}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    })
      .then(async (response) => {
        const body = await parseBody(response);
        if (!response.ok) {
          throw new Error(formatApiError(body, response.status));
        }
        storeAuthTokens(body);
        return body;
      })
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

function redirectExpired() {
  const path = window.location.pathname;
  if (path.startsWith("/login")) {
    return;
  }
  const next = encodeURIComponent(path + window.location.search);
  window.location.assign(`/login?expired=1&next=${next}`);
}

function isAnonymousApi(path) {
  return (
    path.startsWith("/api/public/") ||
    path.startsWith("/api/packages") ||
    path.startsWith("/api/verify/") ||
    path === "/health"
  );
}

export async function apiRequest(method, path, payload, options = {}) {
  const headers = {};
  const token = getToken();
  const skipAuth = options.anonymous || isAnonymousApi(path);
  if (token && !skipAuth) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (payload !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  let response;
  try {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), options.timeoutMs || 12000);
    try {
      response = await fetch(`${API}${path}`, {
        method,
        headers,
        body: payload !== undefined ? JSON.stringify(payload) : undefined,
        signal: controller.signal,
      });
    } finally {
      window.clearTimeout(timer);
    }
  } catch (err) {
    if (err?.name === "AbortError") {
      throw new Error("Request timed out. Make sure the HoneyChain API is running on port 8000.");
    }
    if (!options.skipQueue && method !== "GET") {
      const queue = readQueue();
      queue.push({ method, path, payload, queuedAt: new Date().toISOString() });
      writeQueue(queue);
      throw new Error("Offline — action queued and will retry when the connection returns.");
    }
    throw new Error("Couldn't reach the HoneyChain API. Make sure the backend is running.");
  }
  if (response.status === 401 && !options.skipRefresh && !path.startsWith("/api/auth/login") && !path.startsWith("/api/auth/register") && path !== "/api/auth/refresh") {
    try {
      await refreshAccess();
      return apiRequest(method, path, payload, { ...options, skipRefresh: true });
    } catch {
      clearToken();
      redirectExpired();
      throw new Error("Your session expired. Sign in again.");
    }
  }
  const body = await parseBody(response);
  if (!response.ok) {
    throw new Error(formatApiError(body, response.status));
  }
  return body;
}

export function apiGet(path) {
  return apiRequest("GET", path);
}

export function apiSend(method, path, payload) {
  return apiRequest(method, path, payload);
}

export function apiPost(path, payload) {
  return apiRequest("POST", path, payload);
}

export function qrImageUrl(packageId) {
  return `/api/packages/${packageId}/qr`;
}
