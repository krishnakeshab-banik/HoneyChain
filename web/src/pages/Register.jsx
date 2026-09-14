import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiPost } from "../api";
import { useAuth } from "../auth";
import AuthShell, { FieldError, PasswordField } from "../components/AuthShell";
import { Banner } from "../components/Ui";

export default function Register() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "", display_name: "", email: "", phone: "" });
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [busy, setBusy] = useState(false);

  function setField(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setFieldErrors((prev) => ({ ...prev, [key]: "" }));
  }

  function validate() {
    const next = {};
    if (!form.username.trim()) {
      next.username = "Pick a short username.";
    }
    if (form.password.length < 8) {
      next.password = "Use at least 8 characters.";
    }
    if (!form.display_name.trim()) {
      next.display_name = "Tell us how to greet you.";
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
      await apiPost("/api/auth/register", {
        username: form.username.trim(),
        password: form.password,
        display_name: form.display_name.trim(),
        email: form.email.trim() || null,
        phone: form.phone.trim() || null,
      });
      await login(form.username.trim(), form.password);
      navigate("/app/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell
      kicker="NEW BEEKEEPER"
      title="Create your account"
      lead="Only beekeepers register here. Officers and labs are added by an administrator."
    >
      <form className="card auth-card" onSubmit={onSubmit} noValidate>
        {error && <Banner tone="bad">{error}</Banner>}
        <label htmlFor="username">Username</label>
        <input id="username" value={form.username} onChange={(event) => setField("username", event.target.value)} />
        <FieldError message={fieldErrors.username} />
        <label htmlFor="display_name">Your name</label>
        <input
          id="display_name"
          value={form.display_name}
          onChange={(event) => setField("display_name", event.target.value)}
        />
        <FieldError message={fieldErrors.display_name} />
        <label htmlFor="email">Email (optional)</label>
        <input id="email" value={form.email} onChange={(event) => setField("email", event.target.value)} />
        <label htmlFor="phone">Phone (optional)</label>
        <input id="phone" value={form.phone} onChange={(event) => setField("phone", event.target.value)} />
        <PasswordField
          id="password"
          value={form.password}
          label="Password"
          autoComplete="new-password"
          onChange={(event) => setField("password", event.target.value)}
        />
        <FieldError message={fieldErrors.password} />
        <button className="primary" type="submit" disabled={busy}>
          {busy ? "Creating…" : "Create account"}
        </button>
      </form>
      <p className="muted">
        Already registered? <Link to="/login">Sign in</Link>
      </p>
    </AuthShell>
  );
}
