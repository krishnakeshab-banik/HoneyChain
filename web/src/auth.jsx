import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiGet, apiSend, clearToken, getToken, storeAuthTokens } from "./api";
import { LANG_KEY, LANGUAGES } from "./i18n";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const { i18n } = useTranslation();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));

  useEffect(() => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    apiGet("/api/auth/me")
      .then((next) => {
        setUser(next);
        if (next.language && next.language !== i18n.language) {
          i18n.changeLanguage(next.language);
          window.localStorage.setItem(LANG_KEY, next.language);
        }
      })
      .catch(() => {
        clearToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, [i18n]);

  const value = useMemo(
    () => ({
      user,
      loading,
      role: user?.role || "consumer",
      async login(username, password) {
        const token = await apiSend("POST", "/api/auth/login", { username, password });
        storeAuthTokens(token);
        const me = await apiGet("/api/auth/me");
        setUser(me);
        if (me.language) {
          i18n.changeLanguage(me.language);
          window.localStorage.setItem(LANG_KEY, me.language);
        }
        return me;
      },
      async register(payload) {
        const token = await apiSend("POST", "/api/auth/register", payload);
        storeAuthTokens(token);
        const me = await apiGet("/api/auth/me");
        setUser(me);
        return me;
      },
      logout() {
        const refresh = window.localStorage.getItem("honeychain_refresh");
        if (refresh) {
          apiSend("POST", "/api/auth/logout", { refresh_token: refresh }).catch(() => {});
        }
        clearToken();
        setUser(null);
      },
      async setLanguage(code) {
        if (!LANGUAGES.some((item) => item.code === code)) {
          return;
        }
        i18n.changeLanguage(code);
        window.localStorage.setItem(LANG_KEY, code);
        if (getToken()) {
          const me = await apiSend("PATCH", "/api/auth/me/language", { language: code });
          setUser(me);
        }
      },
    }),
    [user, loading, i18n],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
}
