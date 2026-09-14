import { Navigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../auth";
import { Loading } from "./Ui";

export default function RequireAuth({ roles, children }) {
  const { user, loading, role } = useAuth();
  const location = useLocation();
  const { t } = useTranslation();

  if (loading) {
    return <Loading label={t("common.loading")} />;
  }
  if (!user) {
    const next = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/login?next=${next}`} replace />;
  }
  if (roles && !roles.includes(role)) {
    return <Navigate to="/403" replace />;
  }
  return children;
}
