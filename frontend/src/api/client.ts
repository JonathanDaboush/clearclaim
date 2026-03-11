/**
 * RPC-style API client for the ClearClaim backend.
 *
 * The backend uses a custom HTTP handler where:
 *   POST: body must be { args: [...positional], kwargs?: {...} }
 *   GET:  params are passed as plain query-string key=value pairs
 *
 * There is NO JWT auth — the caller must pass user_id as an argument
 * to any call that requires identity (per the backend controller signatures).
 */
import axios from 'axios';

export const BASE_URL = 'http://localhost:8000';

export const http = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

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
