import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LanguageSelect from "./LanguageSelect";

export default function SiteFooter({ compact = false }) {
  const { t } = useTranslation();
  return (
    <footer className={`site-footer ${compact ? "compact" : ""}`}>
      <p>{t("home.footerAbout")}</p>
      {!compact && <p className="muted">{t("home.footerCredibility")}</p>}
      <p className="footer-links">
        <Link to="/how-it-works">{t("nav.how")}</Link>
        <Link to="/verify">{t("nav.verifyHoney")}</Link>
        <Link to="/market">{t("nav.marketPublic")}</Link>
        <Link to="/staff">{t("nav.admin")}</Link>
        <Link to="/login">{t("nav.login")}</Link>
      </p>
      <div className="footer-meta">
        <LanguageSelect id={compact ? "foot-lang-app" : "foot-lang"} />
        <span className="muted">
          <a href="mailto:honeychain@example.org">{t("home.footerContact")}</a>
          {" · "}© {new Date().getFullYear()} HoneyChain · KVIC Honey Mission
        </span>
      </div>
    </footer>
  );
}
