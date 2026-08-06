import { useState, useRef, useEffect } from "react";
import "./App.css";

const EXT_COLORS = {
  py: "#B15E6C",
  js: "#CF8BA9",
  jsx: "#DCB6D5",
  ts: "#B3B3F1",
  tsx: "#B3B3F1",
  md: "#CEC2FF",
  json: "#DCB6D5",
  css: "#CF8BA9",
};

function extColor(path) {
  const ext = path.split(".").pop();
  return EXT_COLORS[ext] || "#8891A3";
}

const CLONE_STAGES = [
  { key: "cloning", label: "cloning" },
  { key: "reading", label: "reading" },
  { key: "chunking", label: "chunking" },
  { key: "embedding", label: "embedding" },
  { key: "ready", label: "ready" },
];

const EXAMPLE_QUESTIONS = [
  "What does this repo do?",
  "Where is the entry point?",
  "How is auth handled?",
  "Show me the main data models",
];

function App() {
  const [theme, setTheme] = useState("light");

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [repoUrl, setRepoUrl] = useState("");
  const [repoInfo, setRepoInfo] = useState(null);

  const [cloneStage, setCloneStage] = useState(null); // index into CLONE_STAGES while cloning
  const [error, setError] = useState(null);

  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const stageTimers = useRef([]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function toggleTheme() {
    setTheme((t) => (t === "light" ? "dark" : "light"));
  }

  function clearStageTimers() {
    stageTimers.current.forEach((id) => clearTimeout(id));
    stageTimers.current = [];
  }

  // Fake-but-informative progress through the clone/index pipeline while
  // we wait on the backend, so the user sees where things are at.
  function startStageAnimation() {
    clearStageTimers();
    setCloneStage(0);
    const stepDurations = [600, 900, 900, 900]; // ms between stage 0->1->2->3->4
    let elapsed = 0;
    stepDurations.forEach((duration, i) => {
      elapsed += duration;
      const id = setTimeout(() => setCloneStage(i + 1), elapsed);
      stageTimers.current.push(id);
    });
  }

  async function handleClone() {
    if (repoUrl.trim() === "") {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    setError(null);
    setLoading(true);
    startStageAnimation();

    try {
      const response = await fetch("http://127.0.0.1:8000/clone", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data = await response.json();

      clearStageTimers();
      setCloneStage(CLONE_STAGES.length - 1);
      setRepoInfo(data);
      setMessages([]);
      setQuestion("");
    } catch (err) {
      console.error(err);
      clearStageTimers();
      setCloneStage(null);
      setError(
        "Could not analyze repository. Check the URL and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleAsk(overrideQuestion) {
    const askedQuestion = (overrideQuestion ?? question).trim();
    if (askedQuestion === "") return;

    setError(null);
    setLoading(true);
    setQuestion("");

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: askedQuestion }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { role: "user", content: askedQuestion },
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      console.error(err);
      setError("Could not connect to the backend. Is it running?");
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleNewRepo() {
    clearStageTimers();
    setRepoInfo(null);
    setRepoUrl("");
    setMessages([]);
    setQuestion("");
    setError(null);
    setCloneStage(null);
  }

  const showStages = loading && !repoInfo && cloneStage !== null;

  return (
    <div className="terminal-shell" data-theme={theme}>
      <div className="terminal-window">
        {/* Window chrome */}
        <div className="terminal-titlebar">
          <div className="dots">
            <span className="dot dot-red" />
            <span className="dot dot-amber" />
            <span className="dot dot-teal" />
          </div>
          <span className="titlebar-label">codequery — bash</span>
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={
              theme === "light" ? "Switch to dark theme" : "Switch to light theme"
            }
            title={theme === "light" ? "Switch to dark theme" : "Switch to light theme"}
          >
            {theme === "light" ? "🌙" : "☀︎"}
          </button>
        </div>

        <div className="terminal-body">
          {/* Header */}
          <header className="header">
            <h1>
              codequery<span className="cursor">▍</span>
            </h1>
            <p className="subtitle">// ask anything about a codebase</p>
          </header>

          {/* Repo command bar */}
          {!repoInfo && (
            <div className="repo-bar">
              <span className="prompt-glyph">$</span>
              <input
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="git clone https://github.com/owner/repo"
                className="repo-input"
                disabled={loading}
                onKeyDown={(e) => e.key === "Enter" && handleClone()}
              />
              <button
                onClick={handleClone}
                disabled={loading}
                className="run-btn"
              >
                {loading ? "running…" : "run →"}
              </button>
            </div>
          )}

          {/* Clone progress stepper */}
          {showStages && (
            <div className="progress-stages">
              {CLONE_STAGES.map((stage, i) => (
                <div key={stage.key} style={{ display: "flex", alignItems: "center" }}>
                  <div
                    className={
                      "progress-stage " +
                      (i < cloneStage
                        ? "progress-done"
                        : i === cloneStage
                        ? "progress-active"
                        : "")
                    }
                  >
                    <span className="progress-dot" />
                    <span className="progress-label">{stage.label}</span>
                  </div>
                  {i < CLONE_STAGES.length - 1 && (
                    <span className="progress-connector" />
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Error banner */}
          {error && (
            <div className="error-banner">
              <span className="error-glyph">!</span>
              <span className="error-text">{error}</span>
              <button
                type="button"
                className="error-dismiss"
                onClick={() => setError(null)}
                aria-label="Dismiss error"
              >
                ×
              </button>
            </div>
          )}

          {/* Repo status ledger */}
          {repoInfo && (
            <div className="repo-ledger">
              <span className="status-dot" />
              <span className="ledger-item">
                <strong>{repoInfo.owner}</strong>/{repoInfo.repository}
              </span>
              <span className="ledger-sep">·</span>
              <span className="ledger-item">{repoInfo.files} files</span>
              <span className="ledger-sep">·</span>
              <span className="ledger-item">{repoInfo.chunks} chunks</span>
              <span className="ledger-sep">·</span>
              <span className="ledger-ready">ready</span>
              <button
                type="button"
                className="new-repo-btn"
                onClick={handleNewRepo}
              >
                new repository
              </button>
            </div>
          )}

          {/* Chat transcript */}
          <div className="chat-window">
            {messages.length === 0 && !loading && (
              <div className="empty-state">
                {repoInfo ? (
                  <>
                    <p className="empty-state-lead">
                      Type a question below to start querying this repo, or try:
                    </p>
                    <div className="example-grid">
                      {EXAMPLE_QUESTIONS.map((ex) => (
                        <button
                          key={ex}
                          type="button"
                          className="example-chip"
                          onClick={() => handleAsk(ex)}
                        >
                          {ex}
                        </button>
                      ))}
                    </div>
                  </>
                ) : (
                  "Clone a repository above to get started."
                )}
              </div>
            )}

            {messages.map((message, index) =>
              message.role === "user" ? (
                <div key={index} className="line line-user">
                  <span className="glyph">$</span>
                  <span className="line-text">{message.content}</span>
                </div>
              ) : (
                <div key={index} className="line line-assistant">
                  <span className="glyph">&gt;</span>
                  <div className="answer-block">
                    <p className="answer-text">{message.content}</p>

                    {message.sources && message.sources.length > 0 && (
                      <div className="sources">
                        {message.sources.map((source, i) => {
                          const clean = source.replace(
                            "repositories/active_repo",
                            ""
                          );
                          return (
                            <span key={i} className="source-tag">
                              <span
                                className="source-dot"
                                style={{ background: extColor(clean) }}
                              />
                              {clean}
                            </span>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              )
            )}

            {loading && repoInfo && (
              <div className="line line-assistant">
                <span className="glyph">&gt;</span>
                <span className="thinking">
                  thinking<span className="cursor">▍</span>
                </span>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Question input */}
          <div className="ask-bar">
            <span className="prompt-glyph">$</span>
            <input
              ref={inputRef}
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={
                repoInfo ? "ask a question…" : "clone a repo first"
              }
              className="ask-input"
              disabled={!repoInfo || loading}
              onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            />
            <button
              onClick={() => handleAsk()}
              disabled={loading || !repoInfo}
              className="run-btn"
            >
              {loading ? "…" : "ask →"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
