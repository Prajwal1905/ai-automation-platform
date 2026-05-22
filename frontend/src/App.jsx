import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://localhost:8001/api";

function StatCard({ label, value }) {
  return (
    <div
      style={{
        background: "#1e1e2e",
        border: "1px solid #2a2a3e",
        borderRadius: "8px",
        padding: "20px 24px",
        minWidth: "160px",
      }}
    >
      <div style={{ color: "#888", fontSize: "13px", marginBottom: "8px" }}>
        {label}
      </div>
      <div style={{ color: "#fff", fontSize: "28px", fontWeight: "600" }}>
        {value}
      </div>
    </div>
  );
}

function IntentBadge({ intent }) {
  const colors = {
    lead: "#22c55e",
    support: "#ef4444",
    invoice: "#3b82f6",
    other: "#888",
  };
  return (
    <span
      style={{
        background: colors[intent] + "22",
        color: colors[intent],
        padding: "2px 10px",
        borderRadius: "99px",
        fontSize: "12px",
        fontWeight: "500",
      }}
    >
      {intent}
    </span>
  );
}

export default function App() {
  const [stats, setStats] = useState({});
  const [messages, setMessages] = useState([]);
  const [leads, setLeads] = useState([]);
  const [tab, setTab] = useState("messages");

  useEffect(() => {
    axios.get(`${API}/stats`).then((r) => setStats(r.data));
    axios.get(`${API}/messages`).then((r) => setMessages(r.data.messages));
    axios.get(`${API}/leads`).then((r) => setLeads(r.data.leads));
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#13131f",
        color: "#fff",
        fontFamily: "Inter, sans-serif",
        padding: "32px",
      }}
    >
      <h1 style={{ fontSize: "20px", fontWeight: "600", marginBottom: "4px" }}>
        AI Automation Platform
      </h1>
      <p style={{ color: "#666", fontSize: "13px", marginBottom: "32px" }}>
        Live dashboard — messages, leads, and invoices
      </p>

      {/* stats */}
      <div
        style={{
          display: "flex",
          gap: "16px",
          marginBottom: "32px",
          flexWrap: "wrap",
        }}
      >
        <StatCard label="Total Messages" value={stats.total_messages || 0} />
        <StatCard label="Total Leads" value={stats.total_leads || 0} />
        <StatCard label="Total Invoices" value={stats.total_invoices || 0} />
        <StatCard label="High Urgency" value={stats.high_urgency || 0} />
      </div>

      {/* tabs */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "24px" }}>
        {["messages", "leads"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              padding: "8px 20px",
              borderRadius: "6px",
              border: "none",
              cursor: "pointer",
              background: tab === t ? "#6366f1" : "#1e1e2e",
              color: tab === t ? "#fff" : "#888",
              fontSize: "13px",
              fontWeight: "500",
            }}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* messages table */}
      {tab === "messages" && (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ color: "#666", fontSize: "12px", textAlign: "left" }}>
              <th style={{ padding: "8px 12px" }}>Sender</th>
              <th style={{ padding: "8px 12px" }}>Message</th>
              <th style={{ padding: "8px 12px" }}>Intent</th>
              <th style={{ padding: "8px 12px" }}>Urgency</th>
              <th style={{ padding: "8px 12px" }}>Channel</th>
              <th style={{ padding: "8px 12px" }}>Time</th>
            </tr>
          </thead>
          <tbody>
            {messages.map((m, i) => (
              <tr
                key={i}
                style={{
                  borderTop: "1px solid #1e1e2e",
                  fontSize: "13px",
                }}
              >
                <td style={{ padding: "12px" }}>{m.sender}</td>
                <td
                  style={{ padding: "12px", color: "#aaa", maxWidth: "300px" }}
                >
                  {m.message}
                </td>
                <td style={{ padding: "12px" }}>
                  <IntentBadge intent={m.intent} />
                </td>
                <td
                  style={{
                    padding: "12px",
                    color: m.urgency === "high" ? "#ef4444" : "#aaa",
                  }}
                >
                  {m.urgency}
                </td>
                <td style={{ padding: "12px", color: "#aaa" }}>{m.channel}</td>
                <td style={{ padding: "12px", color: "#555" }}>
                  {new Date(m.created_at).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* leads table */}
      {tab === "leads" && (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ color: "#666", fontSize: "12px", textAlign: "left" }}>
              <th style={{ padding: "8px 12px" }}>Name</th>
              <th style={{ padding: "8px 12px" }}>Company</th>
              <th style={{ padding: "8px 12px" }}>Email</th>
              <th style={{ padding: "8px 12px" }}>Source</th>
              <th style={{ padding: "8px 12px" }}>Time</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((l, i) => (
              <tr
                key={i}
                style={{
                  borderTop: "1px solid #1e1e2e",
                  fontSize: "13px",
                }}
              >
                <td style={{ padding: "12px" }}>{l.name}</td>
                <td style={{ padding: "12px" }}>{l.company}</td>
                <td style={{ padding: "12px", color: "#aaa" }}>
                  {l.email || "--"}
                </td>
                <td style={{ padding: "12px", color: "#aaa" }}>{l.source}</td>
                <td style={{ padding: "12px", color: "#555" }}>
                  {new Date(l.created_at).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
