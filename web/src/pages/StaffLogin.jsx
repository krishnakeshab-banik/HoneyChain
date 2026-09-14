import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../auth";
import AuthShell from "../components/AuthShell";
import { Banner } from "../components/Ui";

const STAFF = [
  { roleKey: "roles.officer", username: "officer", password: "Officer123!", dest: "/app/cluster" },
  { roleKey: "roles.lab", username: "lab", password: "Lab123!", dest: "/app/lab" },
  { roleKey: "roles.admin", username: "admin", password: "Admin123!", dest: "/app/dashboard" },
];

export default function StaffLogin() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  async function enter(account) {
    setBusy(account.username);
    setError("");
    try {
      await login(account.username, account.password);
      navigate(account.dest, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy("");
    }
  }

  return (
    <AuthShell kicker={t("staff.kicker")} title={t("staff.title")} lead={t("staff.lead")}>
      {error && <Banner tone="bad">{error}</Banner>}
      <div className="staff-grid">
        {STAFF.map((account) => (
          <button
            key={account.username}
            className="card lift-card staff-card"
            type="button"
            disabled={Boolean(busy)}
            onClick={() => enter(account)}
          >
            <strong>{t(account.roleKey)}</strong>
            <p className="muted">{account.username}</p>
            <span className="primary">{busy === account.username ? t("staff.signing") : t("staff.enter")}</span>
          </button>
        ))}
      </div>
      <p className="muted">
        {t("staff.beekeeperHint")} <Link to="/login">{t("nav.login")}</Link>
      </p>
    </AuthShell>
  );
}
