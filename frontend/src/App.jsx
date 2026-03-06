import { useState } from "react";
import { Bell, LayoutDashboard, LineChart, Menu, Search, Settings, TrendingUp, X } from "lucide-react";

import Sidebar from "./components/layout/Sidebar";
import AlertsView from "./views/AlertsView";
import DashboardView from "./views/DashboardView";
import PlaceholderView from "./views/PlaceholderView";
import QueryView from "./views/QueryView";

const navItems = [
  { id: "dashboard", label: "系统概览", icon: LayoutDashboard },
  { id: "query", label: "数据查询", icon: Search },
  { id: "analysis", label: "统计分析", icon: LineChart },
  { id: "alerts", label: "预测预警", icon: Bell },
  { id: "settings", label: "系统管理", icon: Settings },
];

export default function App() {
  const [currentView, setCurrentView] = useState("dashboard");
  const [menuOpen, setMenuOpen] = useState(false);

  function renderView() {
    switch (currentView) {
      case "dashboard":
        return <DashboardView />;
      case "query":
        return <QueryView />;
      case "alerts":
        return <AlertsView />;
      case "analysis":
        return (
          <PlaceholderView
            title="统计分析模块"
            description="这一页已经预留给同比环比、区域热力分布、季节性分解和多品类对比分析。下一步可以接入 ECharts 完成更完整的论文展示。"
          />
        );
      case "settings":
        return (
          <PlaceholderView
            title="系统管理模块"
            description="这里建议继续补用户登录、数据源配置、定时采集任务、任务日志和报表导出，让系统从演示原型升级为可答辩的完整项目。"
          />
        );
      default:
        return null;
    }
  }

  return (
    <div className="flex min-h-screen bg-[var(--md-background)] text-[var(--md-on-background)]">
      <div className="fixed left-0 top-0 z-20 hidden h-screen lg:block">
        <Sidebar navItems={navItems} currentView={currentView} setCurrentView={setCurrentView} />
      </div>

      {menuOpen ? (
        <div className="fixed inset-0 z-30 bg-[#1C1B1F]/30 backdrop-blur-sm lg:hidden" onClick={() => setMenuOpen(false)}>
          <div className="h-full w-72" onClick={(event) => event.stopPropagation()}>
            <Sidebar navItems={navItems} currentView={currentView} setCurrentView={setCurrentView} onClose={() => setMenuOpen(false)} />
          </div>
        </div>
      ) : null}

      <div className="flex min-h-screen flex-1 flex-col lg:ml-72">
        <header className="sticky top-0 z-10 border-b border-white/50 bg-[var(--md-background)]/85 px-4 py-4 backdrop-blur-sm lg:hidden">
          <div className="flex items-center justify-between">
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
                  <p className="text-xs text-[#49454F]">毕业设计系统原型</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="relative flex-1 overflow-y-auto p-4 md:p-8 xl:p-10">
          <div className="mx-auto max-w-7xl">{renderView()}</div>
        </main>
      </div>
    </div>
  );
}
