import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';

export interface Session {
  user_id: string;
  email: string;
  totp_secret: string;
  device_id: string;
  verification_status: string;
  // JWT tokens
  access_token: string;
  refresh_token: string;
  expires_at: number;   // Unix timestamp (ms) when access_token expires
}

interface AuthState {
  session: Session | null;
  isAuthenticated: boolean;
  setSession: (s: Session) => void;
  updateSession: (partial: Partial<Session>) => void;
  clearSession: () => void;
}

const AUTH_KEY = 'cc_session';

const AuthContext = createContext<AuthState | null>(null);

function loadSession(): Session | null {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<Session | null>(loadSession);

  const setSession = useCallback((s: Session) => {
    localStorage.setItem(AUTH_KEY, JSON.stringify(s));
    setSessionState(s);
  }, []);

  const updateSession = useCallback((partial: Partial<Session>) => {
    setSessionState((prev) => {
      if (!prev) return prev;
      const updated = { ...prev, ...partial };
      localStorage.setItem(AUTH_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const clearSession = useCallback(() => {
    localStorage.removeItem(AUTH_KEY);
    setSessionState(null);
  }, []);

  // Listen for token refresh events from the axios interceptor
  useEffect(() => {
    const onRefresh = (e: Event) => {
      const updated = (e as CustomEvent<Session>).detail;
      setSessionState(updated);
    };
    const onExpired = () => {
      localStorage.removeItem(AUTH_KEY);
      setSessionState(null);
    };
    window.addEventListener('cc:token_refreshed', onRefresh);
    window.addEventListener('cc:session_expired', onExpired);
    return () => {
      window.removeEventListener('cc:token_refreshed', onRefresh);
      window.removeEventListener('cc:session_expired', onExpired);
    };
  }, []);

  return (
    <AuthContext.Provider value={{ session, isAuthenticated: !!session, setSession, updateSession, clearSession }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthStore(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthStore must be used within AuthProvider');
  return ctx;
}
