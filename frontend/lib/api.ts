const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const BASE = `${API_BASE_URL}/api`;

interface ApiError {
  response: {
    status: number;
    data: any;
  };
}

async function request<T>(
  method: string,
  endpoint: string,
  body?: any,
  retry: boolean = true
): Promise<T> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && retry) {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      localStorage.clear();
      window.location.href = "/auth/login";
      throw { response: { status: 401, data: { detail: "Unauthorized" } } } as ApiError;
    }

    const refreshRes = await fetch(`${BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!refreshRes.ok) {
      localStorage.clear();
      window.location.href = "/auth/login";
      throw { response: { status: 401, data: { detail: "Session expired" } } } as ApiError;
    }

    const tokens = await refreshRes.json();
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);

    return request<T>(method, endpoint, body, false);
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw { response: { status: res.status, data } } as ApiError;
  }

  return data as T;
}

export const api = {
  get: <T>(endpoint: string) => request<T>("GET", endpoint),
  post: <T>(endpoint: string, body?: any) => request<T>("POST", endpoint, body),
  put: <T>(endpoint: string, body?: any) => request<T>("PUT", endpoint, body),
  delete: <T>(endpoint: string) => request<T>("DELETE", endpoint),
};