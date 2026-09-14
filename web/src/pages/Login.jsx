import { useState } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../auth";
import AuthShell, { FieldError, PasswordField } from "../components/AuthShell";
import { Banner } from "../components/Ui";

const ROLE_HOME = {
  beekeeper: "/app/dashboard",
  officer: "/app/cluster",
  lab: "/app/lab",
  admin: "/app/dashboard",
};

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [params] = useSearchParams();
  const intent = params.get("intent");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [busy, setBusy] = useState(false);

  const officerTone = intent === "officer";

  function validate() {
    const next = {};
    if (!username.trim()) {
      next.username = "Enter your username.";
    }
    if (!password) {
      next.password = "Enter your password.";
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
      const nextUser = await login(username.trim(), password);
      const dest = location.state?.from?.pathname || ROLE_HOME[nextUser.role] || "/app/dashboard";
      navigate(dest, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell
      kicker={officerTone ? "KVIC / LAB DESK" : "SIGN IN"}
      title={officerTone ? "Officer and lab sign-in" : "Sign in"}
      lead={
        officerTone
          ? "Use the account an administrator created for your cluster. Beekeepers register separately."
          : "Use the account you were given. Beekeepers can also create one."
      }
    >
      <form className="card auth-card" onSubmit={onSubmit} noValidate>
        {error && <Banner tone="bad">{error}</Banner>}
        <label htmlFor="username">Username</label>
        <input
          id="username"
          value={username}
          onChange={(event) => {
            setUsername(event.target.value);
            setFieldErrors((prev) => ({ ...prev, username: "" }));
          }}
          autoComplete="username"
        />
        <FieldError message={fieldErrors.username} />
        <PasswordField
          id="password"
          value={password}
          label="Password"
          onChange={(event) => {
            setPassword(event.target.value);
            setFieldErrors((prev) => ({ ...prev, password: "" }));
          }}
        />
        <FieldError message={fieldErrors.password} />
        <p>
          <Link to="/forgot-password">Forgot password?</Link>
        </p>
        <button className="primary" type="submit" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="muted">
        Beekeeper without an account? <Link to="/register">Register</Link>
      </p>
    </AuthShell>
  );
}
