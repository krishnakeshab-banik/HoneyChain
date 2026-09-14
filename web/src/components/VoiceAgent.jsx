import { useState } from "react";
import { useTranslation } from "react-i18next";
import { apiPost } from "../api";
import { useAuth } from "../auth";
import { canListen, canSpeak, listenOnce, speak, stopSpeaking } from "../speech";

export default function VoiceAgent() {
  const { user } = useAuth();
  const { i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [transcript, setTranscript] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const language = (i18n.resolvedLanguage || i18n.language || "en").slice(0, 2);

  if (!user) {
    return null;
  }

  async function ask(text) {
    const next = text.trim();
    if (!next) {
      return;
    }
    setBusy(true);
    setError("");
    setTranscript((prev) => [...prev, { role: "you", text: next }]);
    try {
      const result = await apiPost("/api/assistant/ask", { question: next, language });
      setTranscript((prev) => [...prev, { role: "honey", text: result.answer, label: result.ai_label }]);
      speak(result.answer, language);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
      setQuestion("");
    }
  }

  return (
    <>
      <button
        type="button"
        className="voice-fab"
        data-testid="voice-fab"
        aria-label="Ask HoneyChain"
        onClick={() => setOpen((value) => !value)}
      >
        Ask
      </button>
      {open && (
        <div className="voice-panel card" data-testid="voice-panel">
          <strong>Ask HoneyChain</strong>
          <p className="muted">
            Answers use your own hives and harvests
            {canSpeak() ? ", then read back aloud." : ". This browser cannot speak — read the captions."}
          </p>
          <div className="voice-log">
            {transcript.map((line, index) => (
              <p key={`${line.role}-${index}`}>
                <strong>{line.role === "you" ? "You" : "HoneyChain"}:</strong> {line.text}
                {line.label && <span className="ai-tag">{line.label}</span>}
              </p>
            ))}
          </div>
          {error && <p className="field-error">{error}</p>}
          <form
            onSubmit={(event) => {
              event.preventDefault();
              ask(question);
            }}
          >
            <label htmlFor="voice-q">Type a question</label>
            <textarea id="voice-q" rows={2} value={question} onChange={(event) => setQuestion(event.target.value)} />
            <div className="row" style={{ marginTop: 8 }}>
              <button className="primary" type="submit" disabled={busy}>
                {busy ? "Thinking…" : "Ask"}
              </button>
              {canListen() ? (
                <button
                  className="ghost"
                  type="button"
                  disabled={busy}
                  onClick={async () => {
                    try {
                      const heard = await listenOnce(language);
                      setQuestion(heard);
                      await ask(heard);
                    } catch (err) {
                      setError(err.message);
                    }
                  }}
                >
                  Speak
                </button>
              ) : (
                <span className="muted">No microphone on this device — type instead.</span>
              )}
              <button className="ghost" type="button" onClick={stopSpeaking}>
                Stop voice
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}
