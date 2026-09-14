import { Navigate, Route, Routes, useSearchParams } from "react-router-dom";
import AppTopBar from "./components/AppTopBar";
import { BeeDoodle, LeafCorner, Sprig } from "./components/Decor";
import NavSidebar from "./components/NavSidebar";
import OfflineBanner from "./components/OfflineBanner";
import PublicHeader from "./components/PublicHeader";
import RequireAuth from "./components/RequireAuth";
import SiteFooter from "./components/SiteFooter";
import VoiceAgent from "./components/VoiceAgent";
import AdminAnalytics from "./pages/AdminAnalytics";
import Alerts from "./pages/Alerts";
import BeekeeperHome from "./pages/BeekeeperHome";
import CloneWatch from "./pages/CloneWatch";
import ConsumerVerify from "./pages/ConsumerVerify";
import Forbidden from "./pages/Forbidden";
import ForgotPassword from "./pages/ForgotPassword";
import HiveMonitor from "./pages/HiveMonitor";
import Home from "./pages/Home";
import HowItWorks from "./pages/HowItWorks";
import Insights from "./pages/Insights";
import LabDesk from "./pages/LabDesk";
import LedgerIntegrity from "./pages/LedgerIntegrity";
import Login from "./pages/Login";
import Market from "./pages/Market";
import ModelTransparency from "./pages/ModelTransparency";
import PublicModel from "./pages/PublicModel";
import MyHarvests from "./pages/MyHarvests";
import NotFound from "./pages/NotFound";
import OfficerCluster from "./pages/OfficerCluster";
import Overview from "./pages/Overview";
import Profile from "./pages/Profile";
import PublicMarket from "./pages/PublicMarket";
import Register from "./pages/Register";
import ResetPassword from "./pages/ResetPassword";
import SellerReport from "./pages/SellerReport";
import StaffLogin from "./pages/StaffLogin";
import Traceability from "./pages/Traceability";
import UserAdmin from "./pages/UserAdmin";
import { useAuth } from "./auth";
import { ROLE_HOME } from "./navConfig";

function LegacyRedirect() {
  const { user } = useAuth();
  const [params] = useSearchParams();
  const page = params.get("page");
  const packageId = params.get("package_id");
  if (packageId) {
    return <Navigate to={`/verify?package_id=${encodeURIComponent(packageId)}`} replace />;
  }
  const map = {
    home: "/",
    verify: "/verify",
    login: "/login",
    overview: "/app/dashboard",
    monitor: "/app/monitor",
    traceability: "/app/batches",
    insights: "/app/insights",
    market: "/app/market",
    clonewatch: "/app/clonewatch",
    lab: "/app/lab",
    alerts: "/app/alerts",
  };
  if (page && map[page]) {
    return <Navigate to={map[page]} replace />;
  }
  if (user) {
    return <Navigate to={ROLE_HOME[user.role] || "/app/dashboard"} replace />;
  }
  return <Home />;
}

function PublicLayout({ children }) {
  return (
    <div className="public-shell">
      <PublicHeader />
      <div className="public-stage">
        <Sprig className="page-decor page-decor-tl" />
        <BeeDoodle className="page-decor page-decor-tr" />
        <LeafCorner className="page-decor page-decor-bl" />
        <main className="main public-main">{children}</main>
      </div>
      <SiteFooter />
    </div>
  );
}

function AppLayout({ children }) {
  return (
    <div className="shell">
      <NavSidebar />
      <div className="app-column">
        <AppTopBar />
        <OfflineBanner />
        <main className="main">{children}</main>
        <SiteFooter compact />
        <VoiceAgent />
      </div>
    </div>
  );
}

function AdaptiveLayout({ children }) {
  const { user } = useAuth();
  return user ? <AppLayout>{children}</AppLayout> : <PublicLayout>{children}</PublicLayout>;
}

function DashboardHome() {
  const { role } = useAuth();
  if (role === "beekeeper") {
    return <BeekeeperHome />;
  }
  return <Overview canRegister={role === "admin"} />;
}

export default function App() {
  const { role } = useAuth();

  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicLayout>
            <LegacyRedirect />
          </PublicLayout>
        }
      />
      <Route
        path="/how-it-works"
        element={
          <AdaptiveLayout>
            <HowItWorks />
          </AdaptiveLayout>
        }
      />
      <Route
        path="/verify"
        element={
          <AdaptiveLayout>
            <ConsumerVerify />
          </AdaptiveLayout>
        }
      />
      <Route
        path="/market"
        element={
          <AdaptiveLayout>
            <PublicMarket />
          </AdaptiveLayout>
        }
      />
      <Route
        path="/model"
        element={
          <AdaptiveLayout>
            <PublicModel />
          </AdaptiveLayout>
        }
      />
      <Route
        path="/login"
        element={
          <PublicLayout>
            <Login />
          </PublicLayout>
        }
      />
      <Route
        path="/staff"
        element={
          <PublicLayout>
            <StaffLogin />
          </PublicLayout>
        }
      />
      <Route
        path="/register"
        element={
          <PublicLayout>
            <Register />
          </PublicLayout>
        }
      />
      <Route
        path="/forgot-password"
        element={
          <PublicLayout>
            <ForgotPassword />
          </PublicLayout>
        }
      />
      <Route
        path="/reset-password"
        element={
          <PublicLayout>
            <ResetPassword />
          </PublicLayout>
        }
      />
      <Route
        path="/403"
        element={
          <AdaptiveLayout>
            <Forbidden />
          </AdaptiveLayout>
        }
      />
      <Route
        path="/app/profile"
        element={
          <RequireAuth>
            <AppLayout>
              <Profile />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/dashboard"
        element={
          <RequireAuth roles={["beekeeper", "admin"]}>
            <AppLayout>
              <DashboardHome />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/harvests"
        element={
          <RequireAuth roles={["beekeeper"]}>
            <AppLayout>
              <MyHarvests />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/monitor"
        element={
          <RequireAuth roles={["beekeeper", "admin"]}>
            <AppLayout>
              <HiveMonitor />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/insights"
        element={
          <RequireAuth roles={["beekeeper", "officer", "admin"]}>
            <AppLayout>
              <Insights />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/market"
        element={
          <RequireAuth roles={["beekeeper", "officer", "admin"]}>
            <AppLayout>
              <Market />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/cluster"
        element={
          <RequireAuth roles={["officer", "admin"]}>
            <AppLayout>
              <OfficerCluster />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/batches"
        element={
          <RequireAuth roles={["officer", "admin"]}>
            <AppLayout>
              <Traceability role={role} />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/alerts"
        element={
          <RequireAuth roles={["officer", "admin"]}>
            <AppLayout>
              <Alerts />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/lab"
        element={
          <RequireAuth roles={["lab", "admin"]}>
            <AppLayout>
              <LabDesk />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/ledger"
        element={
          <RequireAuth roles={["officer", "admin"]}>
            <AppLayout>
              <LedgerIntegrity />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/clonewatch"
        element={
          <RequireAuth roles={["officer", "admin"]}>
            <AppLayout>
              <CloneWatch />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/users"
        element={
          <RequireAuth roles={["admin"]}>
            <AppLayout>
              <UserAdmin />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/model"
        element={
          <RequireAuth roles={["admin"]}>
            <AppLayout>
              <ModelTransparency />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/analytics"
        element={
          <RequireAuth roles={["admin"]}>
            <AppLayout>
              <AdminAnalytics />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="/app/report"
        element={
          <RequireAuth roles={["beekeeper"]}>
            <AppLayout>
              <SellerReport />
            </AppLayout>
          </RequireAuth>
        }
      />
      <Route
        path="*"
        element={
          <AdaptiveLayout>
            <NotFound />
          </AdaptiveLayout>
        }
      />
    </Routes>
  );
}
