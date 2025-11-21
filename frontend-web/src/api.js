// src/api.js
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 20000,
});

// Attach token from localStorage to all requests
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("chemviz_token");
  if (token) config.headers["Authorization"] = `Token ${token}`;
  return config;
}, (error) => Promise.reject(error));

export default client;
