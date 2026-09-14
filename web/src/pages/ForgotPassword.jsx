import { useState } from "react";
import { Link } from "react-router-dom";
import { apiPost } from "../api";
import AuthShell, { FieldError } from "../components/AuthShell";
import { Banner } from "../components/Ui";

export default function ForgotPassword() {
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    if (!username.trim()) {
      setFieldError("Enter the username you use to sign in.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      setResult(await apiPost("/api/auth/forgot-password", { username: username.trim() }));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell kicker="RESET" title="Forgot password" lead="We'll give you a reset code if that username exists.">
      <form className="card auth-card" onSubmit={onSubmit} noValidate>
        {error && <Banner tone="bad">{error}</Banner>}
        {result && (
          <Banner tone="good">
            {result.detail || result.message}
            {result.reset_code && (
              <p>
                Demo reset code: <strong>{result.reset_code}</strong>.{" "}
                <Link to={`/reset-password?username=${encodeURIComponent(username)}`}>Continue to reset</Link>
              </p>
            )}
          </Banner>
        )}
        <label htmlFor="username">Username</label>
        <input
          id="username"
          value={username}
          onChange={(event) => {
            setUsername(event.target.value);
            setFieldError("");
          }}
        />
        <FieldError message={fieldError} />
        <button className="primary" type="submit" disabled={busy}>
          {busy ? "Sending…" : "Request reset"}
        </button>
      </form>
      <p className="muted">
        Remembered it? <Link to="/login">Back to sign in</Link>
      </p>
    </AuthShell>
  );
}
