import { createContext, useContext, useEffect, useState } from "react";

import { api, clearStoredSession, getStoredSession, persistSession } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => getStoredSession());
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let active = true;

    async function restoreSession() {
      if (!session?.token) {
        if (active) {
          setReady(true);
        }
        return;
      }

      try {
        const user = session.user || (await api.getCurrentUser());
        if (!active) {
          return;
        }

        const nextSession = {
          token: session.token,
          expiresAt: session.expiresAt,
          user,
        };
        persistSession(nextSession);
        setSession(nextSession);
      } catch {
        if (!active) {
          return;
        }
        clearStoredSession();
        setSession(null);
      }

      if (active) {
        setReady(true);
      }
    }

    restoreSession();
    return () => {
      active = false;
    };
  }, [session?.token]);

  async function login(credentials) {
    const payload = await api.login(credentials);
    const nextSession = {
      token: payload.access_token,
      expiresAt: payload.expires_at,
      user: payload.user,
    };
    persistSession(nextSession);
    setSession(nextSession);
    setReady(true);
    return payload;
  }

  async function logout() {
    try {
      await api.logout();
    } catch {
      // ignore logout errors from expired sessions
    }
    clearStoredSession();
    setSession(null);
    setReady(true);
  }

  return (
    <AuthContext.Provider
      value={{
        ready,
        user: session?.user || null,
        token: session?.token || null,
        expiresAt: session?.expiresAt || null,
        isAuthenticated: Boolean(session?.token),
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth 必须在 AuthProvider 内使用");
  }
  return context;
}
