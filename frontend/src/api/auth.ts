const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export interface AuthTokens {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  role: string;
}

export interface SignupPayload {
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = err?.detail;
    const message = Array.isArray(detail)
      ? detail
          .map((item) => {
            if (typeof item === 'string') return item;
            if (item && typeof item === 'object') {
              return item.msg ?? item.message ?? JSON.stringify(item);
            }
            return String(item);
          })
          .join(', ')
      : typeof detail === 'string'
        ? detail
        : err?.message ?? 'Request failed';
    throw new Error(message);
  }
  return res.json();
}

export async function signup(payload: SignupPayload): Promise<AuthTokens> {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload),
  });
  return handleResponse<AuthTokens>(res);
}

export async function login(payload: LoginPayload): Promise<AuthTokens> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload),
  });
  return handleResponse<AuthTokens>(res);
}

export async function logout(): Promise<void> {
  await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' });
}

export async function refreshToken(): Promise<AuthTokens | null> {
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!res.ok) return null;
  return res.json();
}

export async function requestPasswordReset(email: string): Promise<void> {
  await fetch(`${API_BASE}/auth/password-reset/request`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
}
