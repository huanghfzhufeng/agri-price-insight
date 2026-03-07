import { useState } from "react";
import { Bell, LineChart, Menu, Search, Settings, TrendingUp, X } from "lucide-react";
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";

import Sidebar from "./components/layout/Sidebar";
import { useAuth } from "./context/AuthContext";
import AlertsView from "./views/AlertsView";
import AnalysisView from "./views/AnalysisView";
import DashboardView from "./views/DashboardView";
import LoginView from "./views/LoginView";
import QueryView from "./views/QueryView";
import SystemManagementView from "./views/SystemManagementView";

const navItems = [
  { to: "/dashboard", label: "系统概览", icon: TrendingUp },
  { to: "/query", label: "数据查询", icon: Search },
  { to: "/analysis", label: "统计分析", icon: LineChart },
  { to: "/alerts", label: "预测预警", icon: Bell },
  { to: "/settings", label: "系统管理", icon: Settings },
];

function ProtectedLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { logout, user } = useAuth();
  const location = useLocation();

  return (
    <div className="flex min-h-screen bg-[var(--md-background)] text-[var(--md-on-background)]">
      <div className="fixed left-0 top-0 z-20 hidden h-screen lg:block">
        <Sidebar navItems={navItems} user={user} onLogout={logout} />
      </div>

      {menuOpen ? (
        <div className="fixed inset-0 z-30 bg-[#1C1B1F]/30 backdrop-blur-sm lg:hidden" onClick={() => setMenuOpen(false)}>
          <div className="h-full w-72" onClick={(event) => event.stopPropagation()}>
            <Sidebar navItems={navItems} user={user} onLogout={logout} onClose={() => setMenuOpen(false)} />
          </div>
        </div>
      ) : null}

      <div className="flex min-h-screen flex-1 flex-col lg:ml-72">
        <header className="sticky top-0 z-10 border-b border-white/50 bg-[var(--md-background)]/88 px-4 py-4 backdrop-blur-sm lg:hidden">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setMenuOpen((open) => !open)}
                className="rounded-full bg-[var(--md-surface-container)] p-3 text-[#1C1B1F]"
              >
                {menuOpen ? <X size={18} /> : <Menu size={18} />}
              </button>
              <div className="flex items-center gap-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--md-primary)] text-white">
                  <TrendingUp size={18} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-[#1C1B1F]">农智行</p>
                  <p className="text-xs text-[#49454F]">
                    {navItems.find((item) => item.to === location.pathname)?.label || "毕业设计系统"}
                  </p>
                </div>
              </div>
            </div>
            <button type="button" onClick={logout} className="text-sm font-medium text-[var(--md-primary)]">
              退出
            </button>
          </div>
        </header>

        <main className="relative flex-1 overflow-y-auto p-4 md:p-8 xl:p-10">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

function ProtectedRoute() {
  const { ready, isAuthenticated } = useAuth();
  const location = useLocation();

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--md-background)]">
        <div className="rounded-[32px] bg-[var(--md-surface-container)] px-8 py-6 shadow-sm">
          <p className="text-sm text-[#49454F]">系统初始化中...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <ProtectedLayout />;
}

function LoginRoute() {
  const { ready, isAuthenticated } = useAuth();

  if (!ready) {
    return null;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <LoginView />;
}

function NotFoundRoute() {
  return <Navigate to="/dashboard" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardView />} />
        <Route path="/query" element={<QueryView />} />
        <Route path="/analysis" element={<AnalysisView />} />
        <Route path="/alerts" element={<AlertsView />} />
        <Route path="/settings" element={<SystemManagementView />} />
      </Route>
      <Route path="*" element={<NotFoundRoute />} />
    </Routes>
  );
}
