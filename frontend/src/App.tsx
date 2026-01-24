import { useState, type FormEvent } from 'react';
import { fixCode } from "./api";
import type { CodeDiff, CodeFixResponse } from "./types";

type ResultTab = "explanation" | "diffs" | "tests" | "meta";

function App() {
  const [code, setCode] = useState("");
  const [filePath, setFilePath] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CodeFixResponse | null>(null);
  const [activeTab, setActiveTab] = useState<ResultTab>("explanation");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveTab("explanation");

    try {
      const payload = {
        code,
        file_path: filePath || null,
      };

      const data = await fixCode(payload);
      setResult(data);
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        "Something went wrong while calling /fix.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const renderDiffs = (diffs: CodeDiff[]) => {
    if (!diffs.length) {
      return <p>No diffs returned by the model.</p>;
    }

    const combined = diffs
      .map((d) => `# File: ${d.filepath}\n${d.diff}`)
      .join("\n\n");

    const copyAllDiffs = async () => {
      try {
        await navigator.clipboard.writeText(combined);
        alert("All diffs copied to clipboard ✅");
      } catch {
        alert("Could not copy diffs.");
      }
    };

    return (
      <div>
        <div style={{ textAlign: "right", marginBottom: "0.5rem" }}>
          <button
            type="button"
            onClick={copyAllDiffs}
            style={{
              padding: "0.35rem 0.7rem",
              borderRadius: "0.375rem",
              border: "none",
              background: "#4b5563",
              color: "#e5e7eb",
              fontSize: "0.85rem",
              cursor: "pointer",
            }}
          >
            Copy all diffs
          </button>
        </div>
        {diffs.map((d, idx) => (
          <div key={idx} style={{ marginBottom: "1rem" }}>
            <h4>{d.filepath}</h4>
            <pre
              style={{
                background: "#1e1e1e",
                color: "#d4d4d4",
                padding: "0.75rem",
                borderRadius: "4px",
                overflowX: "auto",
              }}
            >
              {d.diff}
            </pre>
          </div>
        ))}
      </div>
    );
  };

  const copyTestStub = async () => {
    if (!result?.test_stub) return;
    try {
      await navigator.clipboard.writeText(result.test_stub);
      alert("Test stub copied to clipboard ✅");
    } catch {
      alert("Could not copy test stub.");
    }
  };

  const fillSample = () => {
    const sample = `
def add(a, b):
return a + b

print(add(1, "2"))
`.trim();
    setCode(sample);
  };

  const clearAll = () => {
    setCode("");
    setFilePath("");
    setResult(null);
    setError(null);
  };

  return (
    <div
  style={{
    width: "95%",
    minHeight: "100vh",
    background: "#0f172a",
    color: "#e5e7eb",
    padding: "2rem",
    display: "flex",
    justifyContent: "center",
  }}
>
  <div
    style={{
      width: "100%",
      maxWidth: "1400px",
      background: "#020617",
      borderRadius: "0.75rem",
      padding: "2rem",
      border: "1px solid #1f2937",
      boxShadow: "0 15px 30px rgba(0,0,0,0.4)",
    }}
  >
        <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem" }}>
          🧠 AI Code-Fix Agent
        </h1>
        <p style={{ marginBottom: "1.5rem", color: "#9ca3af" }}>
          Paste your Python code, and the backend LLM will return diffs, tests, and an
          explanation.
        </p>

        <form
          onSubmit={handleSubmit}
          style={{
            marginBottom: "1.5rem",
            display: "grid",
            gap: "1rem",
            gridTemplateColumns: "2fr 3fr",
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            <div>
              <label
                htmlFor="filePath"
                style={{ display: "block", marginBottom: "0.25rem" }}
              >
                File path (optional)
              </label>
              <input
                id="filePath"
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder="e.g. app/main.py"
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "0.375rem",
                  border: "1px solid #374151",
                  background: "#020617",
                  color: "#e5e7eb",
                }}
              />
            </div>

            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                type="button"
                onClick={fillSample}
                style={{
                  flex: 1,
                  padding: "0.45rem 0.7rem",
                  borderRadius: "0.375rem",
                  border: "none",
                  background: "#1d4ed8",
                  color: "#e5e7eb",
                  fontSize: "0.9rem",
                  cursor: "pointer",
                }}
              >
                Fill sample code
              </button>
              <button
                type="button"
                onClick={clearAll}
                style={{
                  flex: 1,
                  padding: "0.45rem 0.7rem",
                  borderRadius: "0.375rem",
                  border: "none",
                  background: "#4b5563",
                  color: "#e5e7eb",
                  fontSize: "0.9rem",
                  cursor: "pointer",
                }}
              >
                Clear
              </button>
            </div>

            <button
              type="submit"
              disabled={loading || !code.trim()}
              style={{
                padding: "0.6rem 1.2rem",
                borderRadius: "0.375rem",
                border: "none",
                background: loading || !code.trim() ? "#6b7280" : "#22c55e",
                color: "#020617",
                fontWeight: 600,
                cursor: loading || !code.trim() ? "not-allowed" : "pointer",
              }}
            >
              {loading ? "Fixing..." : "Fix Code"}
            </button>
          </div>

          <div>
            <label
              htmlFor="code"
              style={{ display: "block", marginBottom: "0.25rem" }}
            >
              Code
            </label>
            <textarea
              id="code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Paste your Python code here..."
              rows={14}
              style={{
                width: "100%",
                padding: "0.75rem",
                borderRadius: "0.375rem",
                border: "1px solid #374151",
                background: "#020617",
                color: "#e5e7eb",
                fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco",
              }}
            />
          </div>
        </form>

        {error && (
          <div
            style={{
              marginBottom: "1rem",
              padding: "0.75rem",
              borderRadius: "0.375rem",
              background: "#7f1d1d",
              color: "#fee2e2",
            }}
          >
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div>
            {/* Tab header */}
            <div
              style={{
                display: "flex",
                borderBottom: "1px solid #1f2937",
                marginBottom: "0.75rem",
              }}
            >
              {(
                [
                  ["explanation", "Explanation"],
                  ["diffs", "Diffs"],
                  ["tests", "Test Stub"],
                  ["meta", "Meta"],
                ] as [ResultTab, string][]
              ).map(([tab, label]) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: "0.5rem 0.9rem",
                    border: "none",
                    borderBottom:
                      activeTab === tab ? "2px solid #22c55e" : "2px solid transparent",
                    background: "transparent",
                    color: activeTab === tab ? "#e5e7eb" : "#9ca3af",
                    cursor: "pointer",
                    fontSize: "0.95rem",
                  }}
                >
                  {label}
                </button>
              ))}
            </div>

            {/* Tab content */}
            {activeTab === "explanation" && (
              <div style={{ marginBottom: "1.25rem" }}>
                <h2 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>
                  Explanation
                </h2>
                <p style={{ whiteSpace: "pre-wrap", color: "#d1d5db" }}>
                  {result.explanation || "No explanation provided."}
                </p>
              </div>
            )}

            {activeTab === "diffs" && (
              <div style={{ marginBottom: "1.25rem" }}>
                <h2 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>Diffs</h2>
                {renderDiffs(result.diffs)}
              </div>
            )}

            {activeTab === "tests" && (
              <div style={{ marginBottom: "1.25rem" }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "0.5rem",
                  }}
                >
                  <h2 style={{ fontSize: "1.25rem" }}>Test Stub</h2>
                  <button
                    type="button"
                    onClick={copyTestStub}
                    disabled={!result.test_stub}
                    style={{
                      padding: "0.35rem 0.7rem",
                      borderRadius: "0.375rem",
                      border: "none",
                      background: result.test_stub ? "#4b5563" : "#374151",
                      color: "#e5e7eb",
                      fontSize: "0.85rem",
                      cursor: result.test_stub ? "pointer" : "not-allowed",
                    }}
                  >
                    Copy
                  </button>
                </div>
                <pre
                  style={{
                    background: "#020617",
                    color: "#e5e7eb",
                    padding: "0.75rem",
                    borderRadius: "0.375rem",
                    overflowX: "auto",
                  }}
                >
                  {result.test_stub || "# No test stub returned."}
                </pre>
              </div>
            )}

            {activeTab === "meta" && (
              <div style={{ marginBottom: "1.25rem" }}>
                <h2 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>Meta</h2>
                <p style={{ marginBottom: "0.4rem", color: "#9ca3af" }}>
                  Model: <strong>{result.model_used}</strong>
                </p>
                {result.token_usage && (
                  <pre
                    style={{
                      background: "#020617",
                      color: "#e5e7eb",
                      padding: "0.75rem",
                      borderRadius: "0.375rem",
                      overflowX: "auto",
                    }}
                  >
                    {JSON.stringify(result.token_usage, null, 2)}
                  </pre>
                )}
                {!result.token_usage && <p>No token usage info returned.</p>}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
