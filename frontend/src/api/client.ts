/**
 * RPC-style API client for the ClearClaim backend.
 *
 * POST: body = { args: [...positional], kwargs?: {...} }
 * GET:  params are plain query-string key=value pairs
 *
 * All protected routes require an Authorization: Bearer <access_token> header.
 * The interceptor below auto-refreshes the access token when it expires.
 */
import axios, { type InternalAxiosRequestConfig } from 'axios';

export const BASE_URL = 'http://localhost:8080';

export const http = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ── Request interceptor — attach Bearer token ──────────────────────────────
http.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  try {
    const raw = localStorage.getItem('cc_session');
    if (raw) {
      const session = JSON.parse(raw);
      if (session?.access_token) {
        config.headers = config.headers ?? {};
        config.headers['Authorization'] = `Bearer ${session.access_token}`;
      }
    }
  } catch {
    // ignore
  }
  return config;
});

// ── Response interceptor — refresh on 401 ─────────────────────────────────
let _refreshing: Promise<string | null> | null = null;

http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config as InternalAxiosRequestConfig & { _retried?: boolean };
    if (error.response?.status !== 401 || original._retried) {
      return Promise.reject(error);
    }
    original._retried = true;

    // Attempt token refresh — deduplicate concurrent requests
    if (!_refreshing) {
      _refreshing = (async () => {
        try {
          const raw = localStorage.getItem('cc_session');
          if (!raw) return null;
          const session = JSON.parse(raw);
          if (!session?.refresh_token) return null;

          const res = await axios.post<{ access_token: string; expires_in: number }>(
            `${BASE_URL}/auth/refresh`,
            { args: [session.refresh_token] },
            { headers: { 'Content-Type': 'application/json' } },
          );
          const { access_token, expires_in } = res.data;
          const updated = {
            ...session,
            access_token,
            expires_at: Date.now() + expires_in * 1000,
          };
          localStorage.setItem('cc_session', JSON.stringify(updated));
          // Update React state via a custom event so AuthProvider picks it up
          window.dispatchEvent(new CustomEvent('cc:token_refreshed', { detail: updated }));
          return access_token;
        } catch {
          // Refresh failed — force sign-out
          localStorage.removeItem('cc_session');
          window.dispatchEvent(new Event('cc:session_expired'));
          return null;
        } finally {
          _refreshing = null;
        }
      })();
    }

    const newToken = await _refreshing;
    if (!newToken) return Promise.reject(error);

    original.headers = original.headers ?? {};
    original.headers['Authorization'] = `Bearer ${newToken}`;
    return http(original);
  },
);

/** POST a function call: POST /path  body = { args: [...] } */
export async function rpcPost<T = unknown>(path: string, args: unknown[] = []): Promise<T> {
  const res = await http.post<T>(path, { args });
  return res.data;
}

/** GET a function call: GET /path?key=val&… */
export async function rpcGet<T = unknown>(path: string, params: Record<string, string> = {}): Promise<T> {
  const res = await http.get<T>(path, { params });
  return res.data;
}
