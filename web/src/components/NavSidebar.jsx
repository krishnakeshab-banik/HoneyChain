import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../auth";
import { ROLE_NAV } from "../navConfig";
import { HexIcon, IconChain, IconHive, IconMarket, IconQr, IconSensor, IconYield } from "./Icons";

const ICONS = {
  "/app/dashboard": IconHive,
  "/app/harvests": IconHive,
  "/app/monitor": IconSensor,
  "/app/insights": IconYield,
  "/app/market": IconMarket,
  "/app/cluster": IconHive,
  "/app/batches": IconChain,
  "/app/alerts": IconSensor,
  "/app/lab": IconSensor,
  "/app/ledger": IconChain,
  "/app/clonewatch": IconQr,
  "/app/users": IconHive,
  "/verify": IconQr,
};

export default function NavSidebar() {
  const { t } = useTranslation();
  const { role } = useAuth();
  const items = ROLE_NAV[role] || ROLE_NAV.consumer;

  return (
    <nav className="nav" aria-label="HoneyChain modules">
      <p className="brand">{t("brand.name")}</p>
      <p>{t("brand.tagline")}</p>
      {items.map((item) => {
        const Icon = ICONS[item.to] || IconHive;
        return (
          <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? "active" : "")} end={item.to === "/"}>
            <HexIcon size={22}>
              <Icon />
            </HexIcon>
            {t(item.key)}
          </NavLink>
        );
      })}
    </nav>
  );
}
