import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { apiGet } from "../api";
import { useAuth } from "../auth";
import { useTour } from "./GuidedTour";
import { IconBell, IconSearch } from "./Icons";
import LanguageSelect from "./LanguageSelect";
import { ROLE_NAV } from "../navConfig";

export default function AppTopBar() {
  const { t } = useTranslation();
  const { user, role, logout } = useAuth();
  const { startTour } = useTour();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [notes, setNotes] = useState([]);
  const [showNotes, setShowNotes] = useState(false);
  const items = ROLE_NAV[role] || [];

  useEffect(() => {
    if (!user) {
      return;
    }
    const load = [];
    if (["officer", "admin", "beekeeper"].includes(role)) {
      load.push(apiGet("/api/alerts").catch(() => []));
    }
    Promise.all(load).then(([alerts]) => {
      setNotes((alerts || []).slice(0, 5));
    });
  }, [user, role]);

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) {
      return [];
    }
    return items.filter((item) => t(item.key).toLowerCase().includes(q));
  }, [query, items, t]);

  return (
    <header className="app-topbar">
      <form
        className="quick-jump"
        onSubmit={(event) => {
          event.preventDefault();
          if (matches[0]) {
            navigate(matches[0].to);
            setQuery("");
          }
        }}
      >
        <IconSearch />
        <input
          id="quick-jump"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Jump to a page…"
        />
        {matches.length > 0 && (
          <div className="jump-list">
            {matches.map((item) => (
              <button
                key={item.to}
                type="button"
                onClick={() => {
                  navigate(item.to);
                  setQuery("");
                }}
              >
                {t(item.key)}
              </button>
            ))}
          </div>
        )}
      </form>
      <div className="topbar-right">
        <button type="button" className="icon-btn" aria-label="Notifications" onClick={() => setShowNotes((v) => !v)}>
          <IconBell />
          {notes.length > 0 && <span className="note-dot">{notes.length}</span>}
        </button>
        {showNotes && (
          <div className="menu-pop">
            {notes.length === 0 ? <p className="muted">No alerts yet.</p> : notes.map((note) => <p key={note.alert_id}>{note.message}</p>)}
          </div>
        )}
        <LanguageSelect id="app-lang" />
        <div className="user-menu">
          <button type="button" className="user-chip" data-tour="help" onClick={() => setOpen((v) => !v)}>
            {user?.display_name} · {t(`roles.${role}`)}
          </button>
          {open && (
            <div className="menu-pop">
              <p className="muted">{user?.username}</p>
              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  navigate("/app/profile");
                }}
              >
                Profile
              </button>
              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  startTour(role);
                }}
              >
                Help / Tour
              </button>
              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  logout();
                  navigate("/");
                }}
              >
                {t("nav.logout")}
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
