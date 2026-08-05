import { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [repoUrl, setRepoUrl] = useState("");
  const [repoInfo, setRepoInfo] = useState(null);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function handleClone() {
    if (repoUrl.trim() === "") {
      alert("Please enter a GitHub repository URL.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/clone", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
        }),
      });

      const data = await response.json();

      setRepoInfo(data);

      // Clear old chat when a new repository is analyzed
      setMessages([]);
      setQuestion("");

      alert(data.message);
    } catch (error) {
      console.error(error);
      alert("Could not analyze repository.");
    } finally {
      setLoading(false);
    }
  }

  async function handleAsk() {
    if (question.trim() === "") {
      alert("Please enter a question.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      const data = await response.json();

      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "user",
          content: question,
        },
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);

      setQuestion("");
    } catch (error) {
      console.error(error);
      alert("Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "40px auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>CodeQuery</h1>

      <p>Ask anything about your GitHub repository.</p>

      {/* Repository Section */}

      <h2>Analyze GitHub Repository</h2>

      <div
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "20px",
        }}
      >
        <input
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/username/repository"
          style={{
            flex: 1,
            padding: "10px",
            fontSize: "16px",
          }}
        />

        <button
          onClick={handleClone}
          disabled={loading}
          style={{
            padding: "10px 20px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Analyzing..." : "Analyze Repository"}
        </button>
      </div>

      {/* Repository Information */}

      {repoInfo && (
        <div
          style={{
            background: "#f7f7f7",
            border: "1px solid #ddd",
            borderRadius: "10px",
            padding: "15px",
            marginBottom: "20px",
          }}
        >
          <h3>📂 Repository Loaded</h3>

          <p>
            <strong>Owner:</strong> {repoInfo.owner}
          </p>

          <p>
            <strong>Repository:</strong> {repoInfo.repository}
          </p>

          <p>
            <strong>Files Indexed:</strong> {repoInfo.files}
          </p>

          <p>
            <strong>Chunks Created:</strong> {repoInfo.chunks}
          </p>

          <p
            style={{
              color: "green",
              fontWeight: "bold",
            }}
          >
            ✅ Ready for Questions
          </p>
        </div>
      )}

      {/* Question Input */}

      <div
        style={{
          display: "flex",
          gap: "10px",
        }}
      >
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          style={{
            flex: 1,
            padding: "10px",
            fontSize: "16px",
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleAsk();
            }
          }}
        />

        <button
          onClick={handleAsk}
          disabled={loading}
          style={{
            padding: "10px 20px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {/* Chat */}

      <div className="chat-window">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${
              message.role === "user" ? "user" : "assistant"
            }`}
          >
            <strong>
              {message.role === "user" ? "👤 You" : "🤖 CodeQuery"}
            </strong>

            <p style={{ whiteSpace: "pre-wrap" }}>{message.content}</p>

            {message.sources && (
              <div style={{ marginTop: "10px" }}>
                <strong>📂 Sources</strong>

                <ul>
                  {message.sources.map((source, i) => (
                    <li key={i}>
                      {source.replace("repositories/active_repo", "")}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}

        {/* Typing Loader */}

        {loading && (
          <div className="loader">
            <strong>🤖 CodeQuery</strong>

            <div className="typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={bottomRef}></div>
      </div>
    </div>
  );
}

export default App;