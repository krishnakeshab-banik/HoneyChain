import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { apiPost } from "../api";
import { useAuth } from "../auth";
import AuthShell, { FieldError, PasswordField } from "../components/AuthShell";
import { Banner } from "../components/Ui";

export default function Register() {
  const { t } = useTranslation();
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
      next.username = t("register.userRequired");
    }
    if (form.password.length < 8) {
      next.password = t("register.passRequired");
    }
    if (!form.display_name.trim()) {
      next.display_name = t("register.nameRequired");
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
      kicker={t("register.kicker")}
      title={t("register.title")}
      lead={t("register.lead")}
    >
      <form className="card auth-card" onSubmit={onSubmit} noValidate>
        {error && <Banner tone="bad">{error}</Banner>}
        <label htmlFor="username">{t("register.username")}</label>
        <input
          id="username"
          value={form.username}
          autoComplete="username"
          placeholder="e.g. dhruv"
          onChange={(event) => setField("username", event.target.value)}
        />
        <p className="muted">This is what you type at Sign in. Avoid spaces.</p>
        <FieldError message={fieldErrors.username} />
        <label htmlFor="display_name">{t("register.name")}</label>
        <input
          id="display_name"
          value={form.display_name}
          onChange={(event) => setField("display_name", event.target.value)}
        />
        <FieldError message={fieldErrors.display_name} />
        <label htmlFor="email">{t("register.email")}</label>
        <input id="email" value={form.email} onChange={(event) => setField("email", event.target.value)} />
        <label htmlFor="phone">{t("register.phone")}</label>
        <input id="phone" value={form.phone} onChange={(event) => setField("phone", event.target.value)} />
        <PasswordField
          id="password"
          value={form.password}
          label={t("register.password")}
          autoComplete="new-password"
          onChange={(event) => setField("password", event.target.value)}
        />
        <FieldError message={fieldErrors.password} />
        <button className="primary" type="submit" disabled={busy}>
          {busy ? t("register.submitting") : t("register.submit")}
        </button>
      </form>
      <p className="muted">
        {t("register.already")} <Link to="/login">{t("nav.login")}</Link>
      </p>
    </AuthShell>
  );
}
