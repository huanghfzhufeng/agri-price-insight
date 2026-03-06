export default function Sidebar({ navItems, currentView, setCurrentView, onClose }) {
  return (
    <aside className="flex h-full w-72 flex-col rounded-r-[32px] bg-[var(--md-surface-container)] p-6 shadow-sm">
      <div className="mb-10 mt-2 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 rotate-3 items-center justify-center rounded-xl bg-[var(--md-primary)] text-white shadow-md">
          <span className="text-lg font-semibold">农</span>
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight text-[#1C1B1F]">农智行</h2>
          <p className="text-xs text-[#49454F]">农产品价格监测系统</p>
        </div>
      </div>

      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                setCurrentView(item.id);
                onClose?.();
              }}
              className={[
                "flex w-full items-center gap-4 rounded-full px-5 py-4 text-left text-sm font-medium transition-all duration-300 active:scale-[0.98]",
                isActive
                  ? "bg-[var(--md-secondary-container)] text-[var(--md-on-secondary-container)]"
                  : "text-[#49454F] hover:bg-[var(--md-surface-container-low)] hover:text-[#1C1B1F]",
              ].join(" ")}
            >
              <item.icon size={20} className={isActive ? "text-[var(--md-on-primary-container)]" : ""} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="mt-auto border-t border-[var(--md-surface-container-low)] pt-6">
        <div className="flex cursor-pointer items-center gap-3 rounded-2xl px-2 py-2 transition-colors hover:bg-[var(--md-surface-container-low)]">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--md-primary)] text-sm font-medium text-white">
            管
          </div>
          <div>
            <p className="text-sm font-medium text-[#1C1B1F]">系统管理员</p>
            <p className="text-xs text-[#49454F]">在线</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
