import { useEffect, useState } from "react";
import { AlertTriangle, ArrowDownRight, ArrowUpRight, Download } from "lucide-react";

import { api } from "../api/client";
import MD3Badge from "../components/ui/MD3Badge";
import MD3Button from "../components/ui/MD3Button";
import MD3Card from "../components/ui/MD3Card";
import { resolveProductImage } from "../data/productImageManifest";
import { buildAreaPath, buildLinePath, getValueDomain } from "../utils/chart";

const chartColors = ["#6750A4", "#386A20", "#B3261E"];

export default function DashboardView() {
  const [dashboard, setDashboard] = useState({ summary: [], trend_series: [], top_changes: [] });
  const [status, setStatus] = useState({ loading: true, error: "" });

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setStatus({ loading: true, error: "" });
      try {
        const data = await api.getDashboard(30);
        if (active) {
          setDashboard(data);
        }
      } catch (error) {
        if (active) {
          setStatus({ loading: false, error: error.message });
        }
        return;
      }

      if (active) {
        setStatus({ loading: false, error: "" });
      }
    }

    loadDashboard();
    return () => {
      active = false;
    };
  }, []);

  const primarySeries = dashboard.trend_series[0]?.points ?? [];
  const domain = getValueDomain(dashboard.trend_series.map((series) => series.points));

  return (
    <div className="page-enter relative space-y-8">
      <div className="pointer-events-none absolute right-0 top-0 -z-10 h-96 w-96 -translate-y-1/2 translate-x-1/4 rounded-full bg-[var(--md-primary)]/10 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-0 -z-10 h-80 w-80 -translate-x-1/4 translate-y-1/4 rounded-full bg-[var(--md-tertiary)]/10 blur-3xl" />

      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="mb-2 text-4xl font-normal tracking-tight text-[#1C1B1F]">系统概览</h1>
          <p className="text-[#49454F]">今日农产品价格监测与分析简报</p>
        </div>
        <MD3Button icon={<Download size={18} />}>导出简报</MD3Button>
      </div>

      {status.error ? <ErrorPanel message={status.error} /> : null}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        {(status.loading ? Array.from({ length: 4 }) : dashboard.summary).map((stat, index) => (
          <MD3Card key={stat?.title || index} className="flex h-40 flex-col justify-between">
            {status.loading ? (
              <div className="space-y-4 animate-pulse">
                <div className="h-4 w-1/2 rounded-full bg-white/60" />
                <div className="h-10 w-2/3 rounded-full bg-white/70" />
                <div className="h-4 w-1/3 rounded-full bg-white/60" />
              </div>
            ) : (
              <>
                <div className="flex items-start justify-between">
                  <h3 className="text-sm font-medium text-[#49454F]">{stat.title}</h3>
                  {stat.alert ? <AlertTriangle className="h-5 w-5 animate-pulse text-[var(--md-error)]" /> : null}
                </div>
                <div>
                  <div className="mb-2 flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-[#1C1B1F]">{stat.value}</span>
                    <span className="text-sm text-[#49454F]">{stat.unit}</span>
                  </div>
                  <div
                    className={[
                      "flex items-center text-sm font-medium",
                      stat.trend_direction === "up"
                        ? "text-[var(--md-success)]"
                        : stat.trend_direction === "down"
                          ? "text-[var(--md-error)]"
                          : "text-[#49454F]",
                    ].join(" ")}
                  >
                    {stat.trend_direction === "up" ? <ArrowUpRight className="mr-1 h-4 w-4" /> : null}
                    {stat.trend_direction === "down" ? <ArrowDownRight className="mr-1 h-4 w-4" /> : null}
                    {stat.trend} 较昨日
                  </div>
                </div>
              </>
            )}
          </MD3Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <MD3Card className="min-h-[420px] xl:col-span-2">
          <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <h2 className="text-2xl font-medium text-[#1C1B1F]">近30天重点品类价格趋势</h2>
            <div className="flex flex-wrap gap-2">
              {dashboard.trend_series.map((series, index) => (
                <MD3Badge key={series.name} color={index === 1 ? "success" : index === 2 ? "error" : "primary"}>
                  {series.name}
                </MD3Badge>
              ))}
            </div>
          </div>

          <div className="chart-panel relative flex min-h-[320px] items-end overflow-hidden rounded-[24px] border border-white/60 bg-white/30 p-6">
            {status.loading ? (
              <div className="h-full w-full animate-pulse rounded-2xl bg-white/50" />
            ) : (
              <svg className="h-full w-full" viewBox="0 0 600 280" preserveAspectRatio="none">
                {primarySeries.length ? (
                  <path d={buildAreaPath(primarySeries, { domain })} fill="url(#seriesGradient)" opacity="0.22" />
                ) : null}

                {dashboard.trend_series.map((series, index) => (
                  <path
                    key={series.name}
                    d={buildLinePath(series.points, { domain })}
                    fill="none"
                    stroke={chartColors[index % chartColors.length]}
                    strokeWidth={index === 0 ? 4 : 3}
                    strokeDasharray={index === 1 ? "0" : index === 2 ? "6 6" : "0"}
                    className={index === 0 ? "path-draw" : ""}
                    opacity={index === 0 ? 1 : 0.72}
                  />
                ))}
                <defs>
                  <linearGradient id="seriesGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#6750A4" stopOpacity="1" />
                    <stop offset="100%" stopColor="#FFFBFE" stopOpacity="0" />
                  </linearGradient>
                </defs>
              </svg>
            )}
          </div>
        </MD3Card>

        <MD3Card className="flex flex-col">
          <h2 className="mb-6 text-xl font-medium text-[#1C1B1F]">今日涨跌幅排行</h2>
          <div className="space-y-4">
            {(status.loading ? Array.from({ length: 5 }) : dashboard.top_changes).map((item, index) =>
              status.loading ? (
                <div key={index} className="h-16 animate-pulse rounded-xl bg-white/50" />
              ) : (
                <div
                  key={`${item.name}-${item.market}`}
                  className="flex cursor-pointer items-center justify-between rounded-xl p-3 transition-colors hover:bg-[var(--md-surface-container-low)]/70"
                >
                  <div className="flex items-center gap-3">
                    <img
                      src={resolveProductImage(item.name).src}
                      alt={resolveProductImage(item.name).alt}
                      className="h-12 w-12 rounded-2xl object-cover shadow-sm"
                      loading="lazy"
                    />
                    <div>
                      <p className="font-medium text-[#1C1B1F]">{item.name}</p>
                      <p className="text-xs text-[#49454F]">{item.market}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{item.price}</p>
                    <p className={item.up ? "text-[var(--md-success)]" : "text-[var(--md-error)]"}>{item.change}</p>
                  </div>
                </div>
              )
            )}
          </div>
          <MD3Button variant="text" className="mt-auto pt-6">
            查看完整榜单
          </MD3Button>
        </MD3Card>
      </div>
    </div>
  );
}

function ErrorPanel({ message }) {
  return (
    <MD3Card className="border border-[var(--md-error)]/20 bg-[var(--md-error-container)]" hoverable={false}>
      <p className="text-sm text-[var(--md-error)]">数据加载失败：{message}</p>
    </MD3Card>
  );
}
