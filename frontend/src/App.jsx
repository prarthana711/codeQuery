import { useState, useRef, useEffect } from "react";
import "./App.css";
function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

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
      // This runs whether the request succeeds or fails
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

      {/* Input Section */}
      <div style={{ display: "flex", gap: "10px" }}>
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

      {/* Chat Messages */}
      <div className="chat-window">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${
              message.role === "user"
                ? "user"
                : "assistant"
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
                      {source.replace("repositories/repo", "")}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}

        {/* Loader */}
        {
          loading && (
            <div className="loader">

              <strong>🤖 CodeQuery</strong>

              <div className="typing">
                <span></span>
                <span></span>
                <span></span>
              </div>

            </div>
          )
        }
        <div ref={bottomRef}></div>
      </div>
    </div>
  );
}

export default App;