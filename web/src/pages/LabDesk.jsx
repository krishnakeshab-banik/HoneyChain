import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiGet, apiSend } from "../api";
import { useAuth } from "../auth";
import { Banner, DataTable, Loading, PageHeader } from "../components/Ui";
import { welcomeLine } from "../greeting";

export default function LabDesk() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [queue, setQueue] = useState([]);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    batch_id: "",
    moisture_pct: 17.2,
    purity_pct: 92,
    result: "pass",
    notes: "",
  });

  async function refresh() {
    const [nextQueue, nextResults] = await Promise.all([apiGet("/api/lab/queue"), apiGet("/api/lab/results")]);
    setQueue(nextQueue.pending_batch_ids || []);
    setResults(nextResults);
    setForm((prev) => ({ ...prev, batch_id: prev.batch_id || nextQueue.pending_batch_ids?.[0] || "" }));
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader
        kicker={t("lab.kicker")}
        title={welcomeLine(user?.display_name, t("lab.title"))}
        purpose={t("lab.purpose")}
      />
      {loading && <Loading label={t("lab.loading")} />}
      {error && (
        <div data-testid="page-error">
          <Banner tone="bad">
            {t("lab.error")} — {error}
          </Banner>
        </div>
      )}
      {notice && (
        <div data-testid="page-notice">
          <Banner tone="good">{notice}</Banner>
        </div>
      )}

      <h2>{t("lab.queue")}</h2>
      {queue.length === 0 && !loading ? (
        <Banner tone="info">{t("lab.empty")}</Banner>
      ) : (
        <ul>
          {queue.map((id) => (
            <li key={id}>
              <button className="ghost" type="button" onClick={() => setForm((prev) => ({ ...prev, batch_id: id }))}>
                {id}
              </button>
            </li>
          ))}
        </ul>
      )}

      <form
        className="card"
        onSubmit={async (event) => {
          event.preventDefault();
          setSaving(true);
          setError("");
          setNotice("");
          try {
            await apiSend("POST", "/api/lab/results", {
              batch_id: form.batch_id,
              moisture_pct: Number(form.moisture_pct),
              purity_pct: Number(form.purity_pct),
              result: form.result,
              notes: form.notes,
            });
            await refresh();
            setNotice(`${t("lab.saved")} ${form.batch_id} → ${form.result}.`);
          } catch (err) {
            setError(err.message);
          } finally {
            setSaving(false);
          }
        }}
      >
        <div className="grid-2">
          <div>
            <label htmlFor="lab_batch">{t("market.batchId")}</label>
            {queue.length > 0 ? (
              <select
                id="lab_batch"
                value={form.batch_id}
                onChange={(event) => setForm((prev) => ({ ...prev, batch_id: event.target.value }))}
              >
                {queue.map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))}
              </select>
            ) : (
              <input
                id="lab_batch"
                value={form.batch_id}
                onChange={(event) => setForm((prev) => ({ ...prev, batch_id: event.target.value }))}
              />
            )}
          </div>
          <div>
            <label htmlFor="moisture_pct">{t("lab.moisture")}</label>
            <input
              id="moisture_pct"
              type="number"
              step="0.1"
              value={form.moisture_pct}
              onChange={(event) => setForm((prev) => ({ ...prev, moisture_pct: event.target.value }))}
            />
          </div>
          <div>
            <label htmlFor="purity_pct">{t("lab.purity")}</label>
            <input
              id="purity_pct"
              type="number"
              step="0.1"
              value={form.purity_pct}
              onChange={(event) => setForm((prev) => ({ ...prev, purity_pct: event.target.value }))}
            />
          </div>
          <div>
            <label htmlFor="lab_result">{t("lab.result")}</label>
            <select
              id="lab_result"
              value={form.result}
              onChange={(event) => setForm((prev) => ({ ...prev, result: event.target.value }))}
            >
              <option value="pass">pass</option>
              <option value="fail">fail</option>
            </select>
          </div>
          <div>
            <label htmlFor="lab_notes">{t("lab.notes")}</label>
            <input id="lab_notes" value={form.notes} onChange={(event) => setForm((prev) => ({ ...prev, notes: event.target.value }))} />
          </div>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <button className="primary" type="submit" disabled={!form.batch_id || saving}>
            {saving ? t("lab.submitting") : t("lab.submit")}
          </button>
        </div>
      </form>

      <h2>{t("lab.history")}</h2>
      {results.length === 0 && !loading ? (
        <Banner tone="info">{t("common.empty")}</Banner>
      ) : (
        <DataTable
          rows={results}
          columns={[
            { key: "result_id", label: "ID" },
            { key: "batch_id", label: "Batch" },
            { key: "moisture_pct", label: t("lab.moisture") },
            { key: "purity_pct", label: t("lab.purity") },
            { key: "result", label: t("lab.result") },
            { key: "inspector", label: "Inspector" },
          ]}
        />
      )}
    </div>
  );
}
