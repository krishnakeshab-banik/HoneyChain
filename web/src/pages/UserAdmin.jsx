import { useEffect, useState } from "react";
import { apiGet, apiSend } from "../api";
import { Banner, DataTable, Loading, PrimaryButton, SectionHeading } from "../components/Ui";

export default function UserAdmin() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    username: "officer2",
    password: "Officer123!",
    display_name: "Field Officer 2",
    role: "officer",
    region: "West Bengal",
    cluster: "West Bengal Producer Cluster",
    email: "",
    phone: "",
  });

  async function refresh() {
    setRows(await apiGet("/api/admin/users"));
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <SectionHeading
        kicker="USER MANAGEMENT"
        title="Create and deactivate staff accounts"
        purpose="Officers, lab inspectors, and admins are created here. Beekeeper self-registration cannot pick these roles."
      />
      {loading && <Loading label="Loading users…" />}
      {error && <Banner tone="bad">Couldn't update users — {error}</Banner>}
      {notice && <Banner tone="good">{notice}</Banner>}

      <form
        className="card"
        onSubmit={async (event) => {
          event.preventDefault();
          setSaving(true);
          setError("");
          setNotice("");
          try {
            const created = await apiSend("POST", "/api/admin/users", form);
            await refresh();
            setNotice(`Created ${created.username} as ${created.role}.`);
          } catch (err) {
            setError(err.message);
          } finally {
            setSaving(false);
          }
        }}
      >
        <div className="grid-2">
          {["username", "password", "display_name", "region", "cluster", "email", "phone"].map((key) => (
            <div key={key}>
              <label htmlFor={key}>{key.replaceAll("_", " ")}</label>
              <input
                id={key}
                type={key === "password" ? "password" : "text"}
                value={form[key]}
                onChange={(event) => setForm((prev) => ({ ...prev, [key]: event.target.value }))}
              />
            </div>
          ))}
          <div>
            <label htmlFor="role">Role</label>
            <select id="role" value={form.role} onChange={(event) => setForm((prev) => ({ ...prev, role: event.target.value }))}>
              <option value="officer">officer</option>
              <option value="lab">lab</option>
              <option value="admin">admin</option>
              <option value="beekeeper">beekeeper</option>
            </select>
          </div>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <PrimaryButton type="submit" disabled={saving}>
            {saving ? "Creating…" : "Create account"}
          </PrimaryButton>
        </div>
      </form>

      {rows.length === 0 && !loading ? (
        <Banner tone="info">No users found.</Banner>
      ) : (
        <DataTable
          rows={rows}
          columns={[
            { key: "username", label: "Username" },
            { key: "display_name", label: "Name" },
            { key: "role", label: "Role" },
            { key: "region", label: "Region" },
            { key: "active", label: "Active" },
            {
              key: "toggle",
              label: "",
              render: (row) => (
                <button
                  className="ghost"
                  type="button"
                  onClick={() =>
                    apiSend("PATCH", `/api/admin/users/${row.username}`, { active: !row.active })
                      .then(refresh)
                      .catch((err) => setError(err.message))
                  }
                >
                  {row.active ? "Deactivate" : "Reactivate"}
                </button>
              ),
            },
          ]}
        />
      )}
    </div>
  );
}
