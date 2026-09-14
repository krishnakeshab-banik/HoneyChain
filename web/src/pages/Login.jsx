import { useState } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
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
  const { t } = useTranslation();
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
      next.username = t("login.userRequired");
    }
    if (!password) {
      next.password = t("login.passRequired");
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
      kicker={officerTone ? t("login.kicker") : t("login.kicker")}
      title={officerTone ? t("login.titleOfficer") : t("login.titleGeneric")}
      lead={t("login.purpose")}
    >
      <form className="card auth-card" onSubmit={onSubmit} noValidate>
        {error && <Banner tone="bad">{error}</Banner>}
        <label htmlFor="username">{t("login.username")}</label>
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
          label={t("login.password")}
          onChange={(event) => {
            setPassword(event.target.value);
            setFieldErrors((prev) => ({ ...prev, password: "" }));
          }}
        />
        <FieldError message={fieldErrors.password} />
        <p>
          <Link to="/forgot-password">{t("login.forgot")}</Link>
        </p>
        <button className="primary" type="submit" disabled={busy}>
          {busy ? t("login.submitting") : t("login.submit")}
        </button>
      </form>
      <p className="muted">
        {t("login.registerTitle")} <Link to="/register">{t("nav.register")}</Link>
      </p>
    </AuthShell>
  );
}
