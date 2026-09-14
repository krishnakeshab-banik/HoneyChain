import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageSelect from "./LanguageSelect";

export default function PublicHeader() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  return (
    <header className="public-header">
      <Link to="/" className="public-wordmark">
        <span className="brand">{t("brand.name")}</span>
        <span className="muted">{t("brand.tagline")}</span>
      </Link>
      <button type="button" className="ghost menu-toggle" onClick={() => setOpen((value) => !value)}>
        {t("nav.menu")}
      </button>
      <nav className={`public-links ${open ? "open" : ""}`} aria-label="Public">
        <NavLink to="/" end>
          {t("nav.home")}
        </NavLink>
        <NavLink to="/how-it-works">{t("nav.how")}</NavLink>
        <NavLink to="/model">{t("nav.model")}</NavLink>
        <NavLink to="/verify">{t("nav.verifyHoney")}</NavLink>
        <NavLink to="/market">{t("nav.marketPublic")}</NavLink>
        <NavLink to="/staff">{t("nav.staff")}</NavLink>
      </nav>
      <div className="public-actions">
        <LanguageSelect id="public-lang" />
        <Link className="ghost staff-entry" to="/staff">
          {t("nav.admin")}
        </Link>
        <Link className="ghost" to="/login">
          {t("nav.login")}
        </Link>
        <Link className="primary" to="/register">
          {t("nav.register")}
        </Link>
      </div>
    </header>
  );
}
