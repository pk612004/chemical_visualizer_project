
import React, { createContext, useEffect, useState } from "react";
import api from "./api";

export const AuthContext = createContext({
  token: null,
  login: async () => {},
  register: async () => {},
  logout: () => {}
});

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("chemviz_token") || null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) localStorage.setItem("chemviz_token", token);
    else localStorage.removeItem("chemviz_token");
  }, [token]);

  const login = async (username, password) => {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);

    const res = await api.post("/auth/api-token-auth/", params);
    const t = res.data.token;
    setToken(t);
    return res.data;
  };

  const register = async (username, password) => {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);

    const res = await api.post("/register/", params);
    const t = res.data.token;
    setToken(t);
    return res.data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, register, logout, user }}>
      {children}
    </AuthContext.Provider>
  );
}
