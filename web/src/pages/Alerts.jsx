import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiGet, apiSend } from "../api";
import { Banner, Loading, PageHeader } from "../components/Ui";

export default function Alerts() {
  const { t } = useTranslation();
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ hive_id: "IN-WB-001", message: "Colony weight dropped — check brood and forage." });

  async function refresh() {
    setRows(await apiGet("/api/alerts"));
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader kicker={t("alerts.kicker")} title={t("alerts.title")} purpose={t("alerts.purpose")} />
      {loading && <Loading label={t("alerts.loading")} />}
      {error && (
        <Banner tone="bad">
          {t("alerts.error")} — {error}
        </Banner>
      )}
      {notice && <Banner tone="good">{notice}</Banner>}

      <form
        className="card"
        onSubmit={async (event) => {
          event.preventDefault();
          setSaving(true);
          setError("");
          setNotice("");
          try {
            await apiSend("POST", "/api/alerts", form);
            await refresh();
            setNotice(t("alerts.queued"));
          } catch (err) {
            setError(err.message);
          } finally {
            setSaving(false);
          }
        }}
      >
        <div className="grid-2">
          <div>
            <label htmlFor="alert_hive">{t("alerts.hive")}</label>
            <input id="alert_hive" value={form.hive_id} onChange={(event) => setForm((prev) => ({ ...prev, hive_id: event.target.value }))} />
          </div>
          <div>
            <label htmlFor="alert_msg">{t("alerts.message")}</label>
            <input id="alert_msg" value={form.message} onChange={(event) => setForm((prev) => ({ ...prev, message: event.target.value }))} />
          </div>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <button className="primary" type="submit" disabled={saving}>
            {saving ? t("alerts.sending") : t("alerts.send")}
          </button>
        </div>
      </form>

      {rows.length === 0 && !loading ? (
        <Banner tone="info">{t("alerts.empty")}</Banner>
      ) : (
        <div className="notice-list">
          {rows.map((row) => (
            <article className="card notice-card" key={row.alert_id}>
              <p className="page-kicker">{row.hive_id}</p>
              <strong>{row.message}</strong>
              <p className="muted">
                {row.created_at} · {row.channel} · {row.alert_id}
              </p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
