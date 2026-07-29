import { createContext, useCallback, useContext, useEffect, useState, ReactNode, createElement } from 'react';
import { login as apiLogin, logout as apiLogout, refreshToken, signup as apiSignup, AuthTokens, LoginPayload, SignupPayload } from '../api/auth';
import { setAccessToken } from '../api/client';

interface AuthState {
  token: string | null;
  user: { id: string; email: string; role: string } | null;
  isLoading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (payload: LoginPayload) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ token: null, user: null, isLoading: true });

  // Update api client token when it changes
  useEffect(() => {
    setAccessToken(state.token);
  }, [state.token]);

  // Handle cross-tab logout events from api/client.ts
  useEffect(() => {
    const handleLogoutEvent = () => {
      setState({ token: null, user: null, isLoading: false });
    };
    window.addEventListener('auth:logout', handleLogoutEvent);
    return () => window.removeEventListener('auth:logout', handleLogoutEvent);
  }, []);

  // Try to restore session via refresh token cookie on mount
  useEffect(() => {
    refreshToken().then((tokens) => {
      if (tokens) {
        setState({
          token: tokens.access_token,
          user: { id: tokens.user_id, email: tokens.email, role: tokens.role },
          isLoading: false,
        });
      } else {
        setState((s) => ({ ...s, isLoading: false }));
      }
    }).catch(() => {
      setState((s) => ({ ...s, isLoading: false }));
    });
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const tokens = await apiLogin(payload);
    setState({ token: tokens.access_token, user: { id: tokens.user_id, email: tokens.email, role: tokens.role }, isLoading: false });
  }, []);

  const signup = useCallback(async (payload: SignupPayload) => {
    const tokens = await apiSignup(payload);
    setState({ token: tokens.access_token, user: { id: tokens.user_id, email: tokens.email, role: tokens.role }, isLoading: false });
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } finally {
      setState({ token: null, user: null, isLoading: false });
    }
  }, []);

  return createElement(AuthContext.Provider, { value: { ...state, login, signup, logout } }, children);
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
