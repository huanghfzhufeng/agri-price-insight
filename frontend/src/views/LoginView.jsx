import { LockKeyhole, UserRound } from "lucide-react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import MD3Button from "../components/ui/MD3Button";
import MD3Input from "../components/ui/MD3Input";
import { useAuth } from "../context/AuthContext";

const defaultCredentials = {
  username: "admin",
  password: "Admin@123456",
};

export default function LoginView() {
  const [credentials, setCredentials] = useState(defaultCredentials);
  const [status, setStatus] = useState({ loading: false, error: "" });
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus({ loading: true, error: "" });
    try {
      await login(credentials);
      const nextPath = location.state?.from?.pathname || "/dashboard";
      navigate(nextPath, { replace: true });
    } catch (error) {
      setStatus({ loading: false, error: error.message });
      return;
    }
    setStatus({ loading: false, error: "" });
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[var(--md-background)] px-4 py-12">
      <div className="pointer-events-none absolute -left-10 top-10 h-80 w-80 rounded-full bg-[var(--md-primary)]/12 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-96 w-96 rounded-full bg-[var(--md-tertiary)]/12 blur-3xl" />

      <div className="grid w-full max-w-6xl overflow-hidden rounded-[40px] border border-white/60 bg-white/45 shadow-xl backdrop-blur md:grid-cols-[1.1fr_0.9fr]">
        <section className="hidden flex-col justify-between bg-[linear-gradient(160deg,rgba(103,80,164,0.96),rgba(54,65,128,0.9))] p-10 text-white md:flex">
          <div>
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/14 text-white shadow-lg">
              <span className="text-2xl font-semibold">农</span>
            </div>
            <h1 className="mt-10 max-w-md text-4xl font-semibold leading-tight">农产品价格数据分析可视化系统</h1>
            <p className="mt-4 max-w-lg text-sm leading-7 text-white/80">
              聚合官方价格简报、月度供需报告、预测预警和多维图表，适合作为毕业设计系统完整展示。
            </p>
          </div>
          <div className="rounded-[28px] border border-white/12 bg-white/10 p-6">
            <p className="text-sm text-white/75">当前演示账号</p>
            <p className="mt-3 text-lg font-medium">admin</p>
            <p className="mt-1 text-sm text-white/75">密码：Admin@123456</p>
          </div>
        </section>

        <section className="p-6 sm:p-10 md:p-12">
          <div className="mx-auto max-w-md">
            <div className="mb-10 md:hidden">
              <p className="text-sm font-medium uppercase tracking-[0.24em] text-[var(--md-primary)]">Agricultural Price Insight</p>
              <h1 className="mt-3 text-3xl font-semibold text-[#1C1B1F]">登录系统</h1>
            </div>
            <div className="mb-8 hidden md:block">
              <p className="text-sm font-medium uppercase tracking-[0.24em] text-[var(--md-primary)]">Control Center</p>
              <h1 className="mt-3 text-3xl font-semibold text-[#1C1B1F]">系统登录</h1>
              <p className="mt-3 text-sm leading-6 text-[#49454F]">登录后可以访问真实采集数据、统计分析图表、预测预警和系统管理模块。</p>
            </div>

            <form className="space-y-5" onSubmit={handleSubmit}>
              <MD3Input
                label="账号"
                placeholder="请输入账号"
                icon={UserRound}
                value={credentials.username}
                onChange={(event) => setCredentials((current) => ({ ...current, username: event.target.value }))}
              />
              <MD3Input
                label="密码"
                type="password"
                placeholder="请输入密码"
                icon={LockKeyhole}
                value={credentials.password}
                onChange={(event) => setCredentials((current) => ({ ...current, password: event.target.value }))}
              />

              {status.error ? <p className="rounded-2xl bg-[var(--md-error-container)] px-4 py-3 text-sm text-[var(--md-error)]">{status.error}</p> : null}

              <MD3Button type="submit" className="w-full justify-center py-3" icon={<LockKeyhole size={18} />}>
                {status.loading ? "登录中..." : "进入系统"}
              </MD3Button>
            </form>

            <div className="mt-8 rounded-[24px] bg-[var(--md-surface-container)] p-5 text-sm text-[#49454F] md:hidden">
              <p className="font-medium text-[#1C1B1F]">演示账号</p>
              <p className="mt-2">admin / Admin@123456</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
