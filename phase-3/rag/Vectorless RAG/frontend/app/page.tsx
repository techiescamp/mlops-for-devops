"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  role: "user" | "ai";
  text: string;
  pathTaken?: Array<{ title: string; node_id: string }>;
  citations?: Array<{ title: string; line_num: number; node_id: string; text: string }>;
}

interface IngestStatus {
  status: "idle" | "running" | "completed" | "failed" | "triggered";
  message: string;
}

const backendUrl = "http://127.0.0.1:8000";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isQuerying, setIsQuerying] = useState(false);
  
  const [ingestStatus, setIngestStatus] = useState<IngestStatus>({
    status: "idle",
    message: "Check index status to begin."
  });

  // Drawer states
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [activeCitation, setActiveCitation] = useState<{
    title: string;
    line_num: number;
    text: string;
  } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${backendUrl}/api/status`);
      const data = await res.json();
      setIngestStatus(data);
    } catch (err) {
      console.error("Failed to fetch status:", err);
    }
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Fetch ingestion status on load
  useEffect(() => {
    const timeout = setTimeout(() => {
      fetchStatus();
    }, 0);
    return () => clearTimeout(timeout);
  }, [fetchStatus]);

  // Poll status when in "running" state
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (ingestStatus.status === "running" || ingestStatus.status === "triggered") {
      interval = setInterval(() => {
        fetchStatus();
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [fetchStatus, ingestStatus.status]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isQuerying) return;

    const userQuery = input.trim();
    setInput("");
    
    // Add user message
    setMessages((prev) => [...prev, { role: "user", text: userQuery }]);
    setIsQuerying(true);

    try {
      const res = await fetch(`${backendUrl}/api/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userQuery }),
      });

      if (!res.ok) {
        throw new Error("Backend query failed");
      }

      const data = await res.json();

      // Add AI response
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: data.answer,
          pathTaken: data.path_taken,
          citations: data.citations,
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: "Sorry, I encountered an error communicating with the reasoning backend. Make sure your local FastAPI backend is running and AWS credentials are valid.",
        },
      ]);
    } finally {
      setIsQuerying(false);
    }
  };

  const openCitationDrawer = (citation: { title: string; line_num: number; text: string }) => {
    setActiveCitation(citation);
    setIsDrawerOpen(true);
  };

  return (
    <div className="app-container">
      {/* Sidebar Controls */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">D</div>
          <div>
            <h1 className="brand-name">DocuMancer AI</h1>
            <p style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase" }}>
              Vectorless RAG
            </p>
          </div>
        </div>

        {/* System parameters */}
        <div style={{ marginTop: "auto", display: "flex", flexDirection: "column", gap: "10px" }}>
          <div style={{ borderTop: "1px solid var(--panel-border)", paddingTop: "16px" }}>
            <div style={{ fontSize: "10px", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: 600, marginBottom: "4px" }}>
              Configured LLM
            </div>
            <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>nova-micro-v1:0</div>
          </div>
          <div>
            <div style={{ fontSize: "10px", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: 600, marginBottom: "4px" }}>
              AWS Target Region
            </div>
            <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>us-west-2</div>
          </div>
          <div>
            <div style={{ fontSize: "10px", textTransform: "uppercase", color: "var(--text-muted)", fontWeight: 600, marginBottom: "4px" }}>
              Target Bucket
            </div>
            <div style={{ fontSize: "13px", color: "var(--text-secondary)", wordBreak: "break-all" }}>
              vectorless-rag-s3
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Interface */}
      <main className="main-chat">
        <header className="chat-header">
          <span
            style={{
              fontSize: "12px",
              padding: "4px 8px",
              borderRadius: "8px",
              background: "rgba(255,255,255,0.05)",
              color: "var(--text-secondary)",
              border: "1px solid var(--panel-border)",
            }}
          >
            Vectorless Retrieval
          </span>
        </header>

        {/* Messages */}
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📖</div>
              <h3 style={{ fontSize: "18px", color: "var(--text-primary)" }}>Ask a question</h3>
              <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                Make sure the documentation index has been ingested on the backend, then ask questions about services, ingresses, or pods.
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message-row ${msg.role} animate-message`}>
                <div className="message-bubble">
                  <div className="message-sender">{msg.role === "user" ? "You" : "DocuMancer Engine"}</div>
                  
                  <div className="markdown-body">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                  </div>

                  {/* Explainability Breadcrumbs */}
                  {msg.pathTaken && msg.pathTaken.length > 0 && (
                    <div className="path-container">
                      <div className="path-title">LLM Index Navigation Path</div>
                      <div className="path-step-list">
                        <span className="path-step">Root</span>
                        {msg.pathTaken.map((path, pIdx) => (
                          <React.Fragment key={pIdx}>
                            <span className="path-arrow">➔</span>
                            <span className="path-step">{path.title}</span>
                          </React.Fragment>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Interactive Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div style={{ marginTop: "12px" }}>
                      <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase" }}>
                        Click to view source page
                      </div>
                      <div className="citations-list">
                        {msg.citations.map((cite, cIdx) => (
                          <button
                            key={cIdx}
                            className="citation-chip"
                            onClick={() => openCitationDrawer(cite)}
                          >
                            📖 {cite.title} (L: {cite.line_num})
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {isQuerying && (
            <div className="message-row ai animate-message">
              <div className="message-bubble" style={{ color: "var(--text-muted)" }}>
                <div className="message-sender">DocuMancer Engine</div>
                <div style={{ display: "flex", gap: "4px", alignItems: "center" }}>
                  <span>Bedrock is traversing index tree...</span>
                  <div className="status-dot running" style={{ width: "6px", height: "6px" }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="chat-input-container">
          <form onSubmit={handleSend} className="chat-input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about Kubernetes concepts (e.g., How does a Service work?)"
              className="chat-input"
              disabled={isQuerying}
            />
            <button type="submit" disabled={isQuerying || !input.trim()} className="chat-send-btn">
              ➔
            </button>
          </form>
        </div>
      </main>

      {/* Slide-out Drawer */}
      <div className={`detail-drawer ${isDrawerOpen ? "open" : ""}`}>
        <div className="drawer-header">
          <h3 style={{ fontSize: "16px", fontWeight: 600 }}>Source Page Document</h3>
          <button className="drawer-close" onClick={() => setIsDrawerOpen(false)}>
            ✕
          </button>
        </div>
        <div className="drawer-content">
          {activeCitation && (
            <>
              <h2 className="drawer-section-title">{activeCitation.title}</h2>
              <div className="drawer-meta">Line number: {activeCitation.line_num}</div>
              <div className="markdown-body drawer-text">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{activeCitation.text}</ReactMarkdown>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
