import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

export interface Session {
  user_id: string;
  email: string;
  totp_secret: string; // stored client-side for TOTP verification calls
  device_id: string;
  verification_status: string;
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
