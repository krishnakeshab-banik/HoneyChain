import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { apiPost } from "../api";
import AuthShell, { FieldError, PasswordField } from "../components/AuthShell";
import { Banner } from "../components/Ui";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [username, setUsername] = useState(params.get("username") || "");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [busy, setBusy] = useState(false);

  function validate() {
    const next = {};
    if (!username.trim()) {
      next.username = "Enter your username.";
    }
    if (!code.trim()) {
      next.code = "Enter the reset code.";
    }
    if (password.length < 8) {
      next.password = "Use at least 8 characters.";
    }
    setFieldErrors(next);
    return Object.keys(next).length === 0;
  }

  async function onSubmit(event) {
    event.preventDefault();
    if (!validate()) {
      return;
    }
    setBusy(true);
    setError("");
    try {
      await apiPost("/api/auth/reset-password", {
        username: username.trim(),
        reset_code: code.trim(),
        new_password: password,
      });
      navigate("/login", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell kicker="RESET" title="Choose a new password" lead="Use the demo code from the previous step.">
      <form className="card auth-card" onSubmit={onSubmit} noValidate>
        {error && <Banner tone="bad">{error}</Banner>}
        <label htmlFor="username">Username</label>
        <input id="username" value={username} onChange={(event) => setUsername(event.target.value)} />
        <FieldError message={fieldErrors.username} />
        <label htmlFor="reset_code">Reset code</label>
        <input id="reset_code" value={code} onChange={(event) => setCode(event.target.value)} />
        <FieldError message={fieldErrors.code} />
        <PasswordField
          id="password"
          value={password}
          label="New password"
          autoComplete="new-password"
          onChange={(event) => setPassword(event.target.value)}
        />
        <FieldError message={fieldErrors.password} />
        <button className="primary" type="submit" disabled={busy}>
          {busy ? "Saving…" : "Save password"}
        </button>
      </form>
      <p className="muted">
        <Link to="/login">Back to sign in</Link>
      </p>
    </AuthShell>
  );
}
