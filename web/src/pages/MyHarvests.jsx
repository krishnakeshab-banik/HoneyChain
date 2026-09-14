import { useEffect, useState } from "react";
import { apiGet, apiSend } from "../api";
import { useAuth } from "../auth";
import EmptyState from "../components/EmptyState";
import NumberStepper from "../components/NumberStepper";
import { Banner, Loading, PrimaryButton, SectionHeading } from "../components/Ui";

function nowIso() {
  return new Date().toISOString();
}

function nextHarvestId() {
  return `HV-${Date.now().toString(36).toUpperCase()}`;
}

export default function MyHarvests() {
  const { user } = useAuth();
  const [rows, setRows] = useState([]);
  const [hives, setHives] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({
    harvest_id: nextHarvestId(),
    hive_id: "",
    raw_weight_kg: 6.2,
    moisture_pct: 17.1,
  });

  async function refresh() {
    const [harvests, mine] = await Promise.all([apiGet("/api/auth/me/harvests"), apiGet("/api/auth/me/hives")]);
    setRows(harvests);
    setHives(mine);
    setForm((prev) => ({ ...prev, hive_id: prev.hive_id || mine[0]?.hive_id || "" }));
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function saveHarvest() {
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const created = await apiSend("POST", "/api/harvests", {
        harvest_id: form.harvest_id,
        hive_id: form.hive_id,
        beekeeper_id: user.beekeeper_id,
        harvested_at: nowIso(),
        raw_weight_kg: Number(form.raw_weight_kg),
        moisture_pct: Number(form.moisture_pct),
      });
      await refresh();
      setForm((prev) => ({ ...prev, harvest_id: nextHarvestId() }));
      setNotice(`Harvest ${created.harvest_id} stored. Sensor-logged weight ${created.sensor_logged_weight_kg} kg.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
      setConfirming(false);
    }
  }

  return (
    <div>
      <SectionHeading
        kicker="MY HARVESTS"
        title="Log and track your harvests"
        purpose="Only harvests from your assigned hives appear here. You can correct a pending harvest before an officer seals it on the ledger."
      />
      {loading && <Loading label="Loading harvests…" />}
      {error && (
        <div data-testid="page-error">
          <Banner tone="bad">Couldn't update harvests — {error}</Banner>
        </div>
      )}
      {notice && (
        <div data-testid="page-notice">
          <Banner tone="good">{notice}</Banner>
        </div>
      )}

      <form
        className="card"
        data-tour="harvest-form"
        onSubmit={(event) => {
          event.preventDefault();
          setConfirming(true);
        }}
      >
        <div className="grid-2">
          <div>
            <label htmlFor="harvest_id">Harvest ID (we filled this)</label>
            <input id="harvest_id" value={form.harvest_id} onChange={(event) => setForm((prev) => ({ ...prev, harvest_id: event.target.value }))} />
          </div>
          <div>
            <label htmlFor="harvest_hive">Hive</label>
            <select id="harvest_hive" value={form.hive_id} onChange={(event) => setForm((prev) => ({ ...prev, hive_id: event.target.value }))}>
              {hives.length === 0 && <option value="">No hive assigned yet</option>}
              {hives.map((hive) => (
                <option key={hive.hive_id} value={hive.hive_id}>
                  {hive.hive_id} · {hive.name}
                </option>
              ))}
            </select>
            {hives.length === 0 && (
              <p className="muted">A hive is being assigned to your account. Refresh this page if the list stays empty.</p>
            )}
          </div>
          <NumberStepper
            id="raw_weight"
            label="Raw harvest weight (kg)"
            value={form.raw_weight_kg}
            onChange={(value) => setForm((prev) => ({ ...prev, raw_weight_kg: value }))}
          />
          <NumberStepper
            id="moisture"
            label="Moisture %"
            value={form.moisture_pct}
            min={0}
            max={30}
            onChange={(value) => setForm((prev) => ({ ...prev, moisture_pct: value }))}
          />
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <PrimaryButton type="submit" disabled={saving || !form.hive_id}>
            Review harvest
          </PrimaryButton>
        </div>
      </form>

      {confirming && (
        <div className="card confirm-card">
          <strong>Check this before we save it</strong>
          <p>
            {form.raw_weight_kg} kg from hive {form.hive_id}, moisture {form.moisture_pct}%. This is not on the ledger
            yet — you can still correct it after saving, until an officer commits a batch.
          </p>
          <div className="row">
            <PrimaryButton type="button" disabled={saving} onClick={saveHarvest}>
              {saving ? "Saving…" : "Create harvest"}
            </PrimaryButton>
            <button className="ghost" type="button" onClick={() => setConfirming(false)}>
              Go back
            </button>
          </div>
        </div>
      )}

      <div data-tour="harvest-status">
        {rows.length === 0 && !loading ? (
          <EmptyState title="No harvests yet">
            {form.hive_id
              ? "Review the form above, then Create harvest. The hive scale reading is stored with the log."
              : "A hive with scale readings is required before you can log a harvest."}
          </EmptyState>
        ) : (
          rows.map((row) => (
            <article className="card notice-card" key={row.harvest_id}>
              <p className="page-kicker">{row.status}</p>
              <strong>
                {row.harvest_id} · {row.raw_weight_kg} kg
              </strong>
              <p className="muted">
                {row.hive_id}
                {row.status_reason ? ` · ${row.status_reason}` : ""}
              </p>
              {row.status === "pending" && (
                <button className="ghost" type="button" onClick={() => setEditing({ ...row })}>
                  Correct this harvest
                </button>
              )}
            </article>
          ))
        )}
      </div>

      {editing && (
        <form
          className="card"
          onSubmit={async (event) => {
            event.preventDefault();
            setSaving(true);
            try {
              await apiSend("PATCH", `/api/harvests/${editing.harvest_id}`, {
                raw_weight_kg: Number(editing.raw_weight_kg),
                moisture_pct: Number(editing.moisture_pct),
              });
              await refresh();
              setNotice(`Harvest ${editing.harvest_id} updated. It is still pending — not on the ledger.`);
              setEditing(null);
            } catch (err) {
              setError(err.message);
            } finally {
              setSaving(false);
            }
          }}
        >
          <strong>Correct {editing.harvest_id}</strong>
          <NumberStepper
            id="edit_weight"
            label="Raw harvest weight (kg)"
            value={editing.raw_weight_kg}
            onChange={(value) => setEditing((prev) => ({ ...prev, raw_weight_kg: value }))}
          />
          <NumberStepper
            id="edit_moisture"
            label="Moisture %"
            value={editing.moisture_pct}
            min={0}
            max={30}
            onChange={(value) => setEditing((prev) => ({ ...prev, moisture_pct: value }))}
          />
          <div className="row" style={{ marginTop: 12 }}>
            <PrimaryButton type="submit" disabled={saving}>
              Save correction
            </PrimaryButton>
            <button className="ghost" type="button" onClick={() => setEditing(null)}>
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
