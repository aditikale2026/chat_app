// src/App.jsx
import { useState, useEffect, useRef } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { useRateLimit } from "./hooks/useRateLimit";
import { useQueryHistory } from "./hooks/useQueryHistory";
import { ragAPIClient } from "./utils/api";

// ─────────────────────────────────────────────────────────────
// Root
// ─────────────────────────────────────────────────────────────
export default function App() {
  return (
    <AuthProvider>
      <Main />
    </AuthProvider>
  );
}

function Main() {
  const { user, loading, sessionExpired, logout, setSessionExpired } = useAuth();

  if (loading) return <FullScreenSpinner />;

  return (
    <div className="app-shell">
      {sessionExpired && (
        <SessionExpiredModal
          onClose={() => setSessionExpired(false)}
          onLogout={logout}
        />
      )}
      {user ? <Dashboard /> : <AuthPage />}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Auth Page — Login / Register tabs
// ─────────────────────────────────────────────────────────────
function AuthPage() {
  const [tab, setTab] = useState("login");   // "login" | "register"
  return (
    <div className="auth-bg">
      <div className="auth-card">
        <div className="auth-logo">
          <span className="logo-icon">⬡</span>
          <span className="logo-text">RAGBase</span>
        </div>
        <div className="auth-tabs">
          <button className={tab === "login"    ? "tab active" : "tab"} onClick={() => setTab("login")}>Sign in</button>
          <button className={tab === "register" ? "tab active" : "tab"} onClick={() => setTab("register")}>Create account</button>
        </div>
        {tab === "login" ? <LoginForm /> : <RegisterForm onSuccess={() => setTab("login")} />}
      </div>
    </div>
  );
}

function LoginForm() {
  const { login } = useAuth();
  const [form, setForm]   = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [busy,  setBusy]  = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      await login(form.username, form.password);
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={submit}>
      <Input label="Username" value={form.username} onChange={(v) => setForm({ ...form, username: v })} autoFocus />
      <Input label="Password" type="password" value={form.password} onChange={(v) => setForm({ ...form, password: v })} />
      {error && <p className="form-error">{error}</p>}
      <button className="btn-primary" disabled={busy}>
        {busy ? <Spinner /> : "Sign in"}
      </button>
    </form>
  );
}

function RegisterForm({ onSuccess }) {
  const { register } = useAuth();
  const [form, setForm]   = useState({ username: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy,  setBusy]  = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) { setError("Passwords do not match"); return; }
    setBusy(true); setError("");
    try {
      await register(form.username, form.password);
      onSuccess?.();
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={submit}>
      <Input label="Username" value={form.username} onChange={(v) => setForm({ ...form, username: v })} autoFocus />
      <Input label="Password" type="password" value={form.password} onChange={(v) => setForm({ ...form, password: v })} />
      <Input label="Confirm password" type="password" value={form.confirm} onChange={(v) => setForm({ ...form, confirm: v })} />
      {error && <p className="form-error">{error}</p>}
      <button className="btn-primary" disabled={busy}>
        {busy ? <Spinner /> : "Create account"}
      </button>
    </form>
  );
}

// ─────────────────────────────────────────────────────────────
// Dashboard
// ─────────────────────────────────────────────────────────────
function Dashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState("query"); // "query" | "upload" | "history"

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="logo-icon">⬡</span>
          <span className="logo-text">RAGBase</span>
        </div>
        <nav className="sidebar-nav">
          {[
            { id: "query",   icon: "🔍", label: "Query" },
            { id: "upload",  icon: "📄", label: "Documents" },
            { id: "history", icon: "🕐", label: "History" },
          ].map(({ id, icon, label }) => (
            <button
              key={id}
              className={`nav-item ${activeTab === id ? "active" : ""}`}
              onClick={() => setActiveTab(id)}
            >
              <span className="nav-icon">{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-chip">
            <span className="user-avatar">{user?.username?.[0]?.toUpperCase()}</span>
            <span className="user-name">{user?.username}</span>
          </div>
          <button className="btn-ghost logout-btn" onClick={logout} title="Logout">
            ⏻
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        {activeTab === "query"   && <QueryPanel />}
        {activeTab === "upload"  && <UploadPanel />}
        {activeTab === "history" && <HistoryPanel />}
      </main>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Query Panel
// ─────────────────────────────────────────────────────────────
function QueryPanel() {
  const { blocked, secondsLeft, recordQuery } = useRateLimit();
  const { addEntry } = useQueryHistory();
  const [query,  setQuery]  = useState("");
  const [result, setResult] = useState(null);
  const [error,  setError]  = useState("");
  const [busy,   setBusy]   = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!query.trim() || busy || blocked) return;
    setBusy(true); setError(""); setResult(null);
    try {
      const { data } = await ragAPIClient.query(query);
      setResult(data);
      recordQuery(); // Record query for rate limiting
      addEntry({ query: data.query, answer: data.answer, mode: data.mode, cachedHit: data.mode === "cache" });
    } catch (err) {
      if (err.response?.status !== 429)
        setError(err.response?.data?.detail || "Query failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="panel">
      <h1 className="panel-title">Ask your documents</h1>
      <p className="panel-sub">Query across all your uploaded documents using AI.</p>

      {blocked && (
        <div className="rate-limit-banner">
          <span className="rl-icon">⏱</span>
          <span>Rate limit reached. Please wait <strong>{secondsLeft}s</strong> before querying again.</span>
          <div className="rl-bar-track">
            <div className="rl-bar-fill" style={{ width: `${(secondsLeft / 60) * 100}%` }} />
          </div>
        </div>
      )}

      <form className="query-form" onSubmit={submit}>
        <textarea
          className="query-input"
          placeholder="e.g. What are the main findings in the uploaded report?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(e); }}}
        />
        <button className="btn-primary query-btn" disabled={busy || blocked || !query.trim()}>
          {busy ? <><Spinner /> Searching…</> : "Search"}
        </button>
      </form>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="result-card">
          <div className="result-header">
            <span className="result-label">Answer</span>
            <CacheBadge mode={result.mode} />
          </div>
          <div className="result-body">{result.answer}</div>
          <div className="result-query-echo">Query: <em>{result.query}</em></div>
        </div>
      )}
    </div>
  );
}

function CacheBadge({ mode }) {
  const isCache = mode === "cache" || mode?.includes("cache");
  return (
    <span className={`cache-badge ${isCache ? "cache-hit" : "cache-miss"}`}>
      {isCache ? "⚡ Cache hit" : "🔄 Live"}
    </span>
  );
}

// ─────────────────────────────────────────────────────────────
// Upload Panel
// ─────────────────────────────────────────────────────────────
const MAX_FILES = 3;

function UploadPanel() {
  const [files,       setFiles]       = useState([]);   // uploaded file records from backend
  const [progress,    setProgress]    = useState(null); // 0–100 or null
  const [error,       setError]       = useState("");
  const [dragOver,    setDragOver]    = useState(false);
  const [loading,     setLoading]     = useState(true);  // fetching files on mount
  const [deleting,    setDeleting]    = useState(null); // doc_id being deleted
  const inputRef = useRef();

  // Fetch files on mount
  useEffect(() => {
    fetchUserFiles();
  }, []);

  const fetchUserFiles = async () => {
    try {
      setLoading(true);
      const { data } = await ragAPIClient.getUserDocuments();
      setFiles(data.documents || []);
      setError("");
    } catch (err) {
      console.error("Failed to fetch files:", err);
      setError(err.response?.data?.detail || "Failed to load your files");
      setFiles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFile = async (file) => {
    if (!file) return;
    if (files.length >= MAX_FILES) {
      setError(`Maximum ${MAX_FILES} documents allowed. Remove one first.`);
      return;
    }
    setError(""); setProgress(0);
    try {
      const { data } = await ragAPIClient.upload(file);
      // Refresh file list from backend
      await fetchUserFiles();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setProgress(null);
    }
  };

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Delete "${filename}"?`)) return;
    try {
      setDeleting(docId);
      setError("");
      await ragAPIClient.deleteDocument(docId);
      // Refresh file list from backend
      await fetchUserFiles();
    } catch (err) {
      setError(err.response?.data?.detail || "Delete failed");
    } finally {
      setDeleting(null);
    }
  };

  const onDrop = (e) => {
    e.preventDefault(); setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="panel">
      <h1 className="panel-title">Documents</h1>
      <p className="panel-sub">Upload up to {MAX_FILES} documents. Supported: PDF, TXT, DOCX, CSV, MD.</p>

      {/* File counter */}
      <div className="file-counter">
        {Array.from({ length: MAX_FILES }).map((_, i) => (
          <div key={i} className={`file-slot ${i < files.length ? "filled" : ""}`} />
        ))}
        <span className="file-counter-label">{files.length}/{MAX_FILES} documents</span>
      </div>

      {/* Drop zone */}
      <div
        className={`dropzone ${dragOver ? "drag-over" : ""} ${files.length >= MAX_FILES ? "disabled" : ""}`}
        onClick={() => files.length < MAX_FILES && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <span className="dz-icon">📂</span>
        <p className="dz-text">
          {files.length >= MAX_FILES
            ? "Document limit reached"
            : "Drop a file here or click to browse"}
        </p>
        <input ref={inputRef} type="file" hidden accept=".pdf,.txt,.docx,.csv,.md"
          onChange={(e) => handleFile(e.target.files[0])} />
      </div>

      {/* Progress bar */}
      {progress !== null && (
        <div className="progress-wrap">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <span className="progress-label">{progress}%</span>
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div style={{ textAlign: 'center', color: 'var(--text-2)', padding: '20px' }}>
          <Spinner /> Loading files...
        </div>
      ) : files.length > 0 ? (
        <ul className="file-list">
          {files.map((f) => (
            <li key={f.doc_id} className="file-item" style={{ opacity: deleting === f.doc_id ? 0.5 : 1 }}>
              <span className="file-icon">📄</span>
              <div className="file-info">
                <span className="file-name">{f.filename}</span>
                <span className="file-meta">{formatTime(f.upload_time)}</span>
              </div>
              <button 
                className="btn-ghost remove-btn"
                onClick={() => handleDelete(f.doc_id, f.filename)}
                disabled={deleting === f.doc_id}
                title="Delete this file"
              >
                {deleting === f.doc_id ? <Spinner /> : "✕"}
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <div className="empty-state">
          <span>📂</span>
          <p>No documents yet. Upload one to get started!</p>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// History Panel
// ─────────────────────────────────────────────────────────────
function HistoryPanel() {
  const { history, clearHistory } = useQueryHistory();

  return (
    <div className="panel">
      <div className="panel-header-row">
        <div>
          <h1 className="panel-title">Query history</h1>
          <p className="panel-sub">Your last {history.length} queries, stored locally.</p>
        </div>
        {history.length > 0 && (
          <button className="btn-ghost danger" onClick={clearHistory}>Clear all</button>
        )}
      </div>

      {history.length === 0 ? (
        <div className="empty-state">
          <span>🔍</span>
          <p>No queries yet. Ask something in the Query tab.</p>
        </div>
      ) : (
        <ul className="history-list">
          {history.map((h) => (
            <li key={h.id} className="history-item">
              <div className="history-header">
                <span className="history-query">{h.query}</span>
                <div className="history-meta">
                  <CacheBadge mode={h.mode} />
                  <span className="history-time">{new Date(h.timestamp).toLocaleString()}</span>
                </div>
              </div>
              <p className="history-answer">{h.answer}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Modals & misc components
// ─────────────────────────────────────────────────────────────
function SessionExpiredModal({ onClose, onLogout }) {
  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-icon">🔒</div>
        <h2 className="modal-title">Session expired</h2>
        <p className="modal-body">Your session has expired. Please sign in again to continue.</p>
        <div className="modal-actions">
          <button className="btn-primary" onClick={onLogout}>Sign in again</button>
          <button className="btn-ghost"   onClick={onClose}>Dismiss</button>
        </div>
      </div>
    </div>
  );
}

function FullScreenSpinner() {
  return (
    <div className="fullscreen-spinner">
      <div className="spinner-ring" />
    </div>
  );
}

function Spinner() {
  return <span className="btn-spinner" />;
}

function Input({ label, type = "text", value, onChange, autoFocus }) {
  return (
    <div className="input-group">
      <label className="input-label">{label}</label>
      <input
        className="input-field"
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoFocus={autoFocus}
        required
      />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Utilities
// ─────────────────────────────────────────────────────────────
function formatBytes(bytes) {
  if (!bytes) return "—";
  const k = 1024;
  const sizes = ["B", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

function formatTime(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString();
}