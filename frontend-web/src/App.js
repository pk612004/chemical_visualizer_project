// src/App.js
import React, { useContext, useEffect, useState } from "react";
import { AuthContext } from "./AuthContext";
import api from "./api";
import "./App.css";

import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Pie, Bar } from "react-chartjs-2";

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function LoginRegister() {
  const { login, register } = useContext(AuthContext);
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      if (isRegister) {
        await register(username.trim(), password);
        setMessage("Registered & logged in");
      } else {
        await login(username.trim(), password);
        setMessage("Logged in");
      }
    } catch (err) {
      const text = err?.response?.data?.detail || err?.message || "Auth error";
      setMessage(text);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-card">
      <h2>{isRegister ? "Register" : "Login"}</h2>
      <form onSubmit={submit}>
        <input
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          type="password"
          required
        />
        <button type="submit" disabled={busy}>
          {isRegister ? "Register & Get Token" : "Login"}
        </button>
      </form>
      <div className="auth-toggle">
        <button onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? "Have an account? Login" : "New user? Register"}
        </button>
      </div>
      {message && <div className="message">{message}</div>}
    </div>
  );
}

function UploadAndView() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [tableRows, setTableRows] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchHistory = async () => {
    try {
      const r = await api.get("/history/");
      // r.data could be array or single object; tests returned object style via Invoke-RestMethod -> normalize
      const data = Array.isArray(r.data) ? r.data : [r.data].filter(Boolean);
      setHistory(data);
    } catch (err) {
      console.error("history err", err);
      setHistory([]);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const onUpload = async () => {
    if (!file) return alert("Choose a CSV file first");
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("name", file.name);
      const res = await api.post("/upload/", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      // res.data has id & summary
      setSummary(res.data.summary || null);
      // fetch table data by downloading CSV (convenience)
      // server provides csv_url in history; we'll fetch and parse in frontend if needed
      await fetchHistory();
      setLoading(false);
    } catch (err) {
      setLoading(false);
      alert("Upload failed: " + (err?.response?.data?.detail || err?.message));
    }
  };

  const loadCsvToTable = async (csvUrl) => {
    // csvUrl may be a relative path like /media/uploads/sample.csv
    const base = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";
    try {
      const r = await fetch(base + csvUrl);
      if (!r.ok) throw new Error("Cannot fetch CSV");
      const text = await r.text();
      const lines = text.trim().split("\n").map((l) => l.split(","));
      const headers = lines[0].map((h) => h.trim());
      const rows = lines.slice(1).map((cols) => {
        const obj = {};
        headers.forEach((h, idx) => (obj[h] = cols[idx]));
        return obj;
      });
      setTableRows(rows);
    } catch (err) {
      console.error("load csv err", err);
      setTableRows([]);
    }
  };

  const downloadPdf = async (id) => {
    if (!id) return alert("No id provided");
    const base = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";
    const token = localStorage.getItem("chemviz_token");
    try {
      const r = await fetch(`${base}/api/generate_pdf/${id}/`, {
        method: "GET",
        headers: { Authorization: `Token ${token}` },
      });
      if (!r.ok) throw new Error("Failed to download PDF");
      const blob = await r.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Download failed: " + err.message);
    }
  };

  // Charts data builders
  const pieData = summary ? {
    labels: Object.keys(summary.type_distribution || {}),
    datasets: [{
      data: Object.values(summary.type_distribution || {}),
      label: "Type distribution",
    }]
  } : null;

  const barData = summary ? {
    labels: Object.keys(summary.averages || {}),
    datasets: [{
      label: "Averages",
      data: Object.values(summary.averages || {}),
    }]
  } : null;

  return (
    <div className="app-body">
      <div className="panel upload-panel">
        <h3>Upload CSV</h3>
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={onUpload} disabled={loading}>{loading ? "Uploading..." : "Upload"}</button>
      </div>

      <div className="panel history-panel">
        <h3>History (last uploads)</h3>
        {history.length === 0 && <div>No uploads yet.</div>}
        {history.map((h) => (
          <div key={h.id} className="history-item">
            <div>
              <strong>{h.name}</strong> <small>({new Date(h.uploaded_at).toLocaleString()})</small>
            </div>
            <div className="history-actions">
              <button onClick={() => { if (h.csv_url) loadCsvToTable(h.csv_url); else alert("CSV URL missing"); }}>
                Load CSV table
              </button>
              <button onClick={() => downloadPdf(h.id)}>Download PDF</button>
            </div>
          </div>
        ))}
      </div>

      <div className="panel summary-panel">
        <h3>Summary</h3>
        {summary ? (
          <>
            <div className="summary-card">
              <div>Total rows: {summary.total}</div>
              <div>Averages:
                <pre className="small-pre">{JSON.stringify(summary.averages, null, 2)}</pre>
              </div>
            </div>

            <div className="charts-row">
              <div className="chart-card">
                <h4>Type distribution</h4>
                {pieData ? <Pie data={pieData} /> : <div>No chart data</div>}
              </div>

              <div className="chart-card">
                <h4>Averages</h4>
                {barData ? <Bar data={barData} /> : <div>No chart data</div>}
              </div>
            </div>
          </>
        ) : (
          <div>No summary yet — upload a CSV to see summary & charts</div>
        )}
      </div>

      <div className="panel table-panel">
        <h3>CSV Table</h3>
        {tableRows.length === 0 ? <div>No CSV loaded</div> : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  {Object.keys(tableRows[0]).map(h => <th key={h}>{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {tableRows.map((r, idx) => (
                  <tr key={idx}>
                    {Object.keys(r).map(k => <td key={k}>{r[k]}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const { token, logout } = useContext(AuthContext);

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Chemical Equipment Visualizer</h1>
        {token ? (
          <div>
            <button onClick={logout}>Logout</button>
          </div>
        ) : null}
      </header>

      <main>
        {!token ? <LoginRegister /> : <UploadAndView />}
      </main>

      <footer className="app-footer">
        <small>Frontend demo — Dev use only. Set REACT_APP_API_BASE if backend on different host.</small>
      </footer>
    </div>
  );
}
