import { useEffect, useState } from "react";
import { Settings, TrendingUp } from "lucide-react";

import { api } from "../api/client";
import MD3Badge from "../components/ui/MD3Badge";
import MD3Button from "../components/ui/MD3Button";
import MD3Card from "../components/ui/MD3Card";
import { buildForecastBand, buildLinePath, getValueDomain, getYCoordinate } from "../utils/chart";
import { timeAgo } from "../utils/formatters";

const forecastDaysOptions = [7, 30, 90];

export default function AlertsView() {
  const [days, setDays] = useState(30);
  const [alertData, setAlertData] = useState([]);
  const [forecast, setForecast] = useState({
    product: "大蒜",
    market: "全国均价",
    model_name: "",
    mape: 0,
    rmse: 0,
    history: [],
    forecast: [],
    insight: "",
  });
  const [status, setStatus] = useState({ loading: true, error: "" });

  useEffect(() => {
    let active = true;

    async function loadPageData() {
      setStatus({ loading: true, error: "" });
      try {
        const [alertsResponse, forecastResponse] = await Promise.all([api.getAlerts(), api.getForecast("大蒜", days)]);
        if (active) {
          setAlertData(alertsResponse.items);
          setForecast(forecastResponse);
          setStatus({ loading: false, error: "" });
        }
      } catch (error) {
        if (active) {
          setStatus({ loading: false, error: error.message });
        }
      }
    }

    loadPageData();
    return () => {
      active = false;
    };
  }, [days]);

  const mergedSeries = [...forecast.history, ...forecast.forecast];
  const domain = getValueDomain([mergedSeries]);
  const thresholdLine =
    mergedSeries.length > 0
      ? Math.max(...mergedSeries.map((point) => point.upper_bound ?? point.value)) - 0.1
      : 0;
  const thresholdY = thresholdLine ? getYCoordinate(thresholdLine, domain) : 0;

  return (
    <div className="page-enter relative space-y-8">
      <div className="pointer-events-none absolute right-10 top-20 -z-10 h-80 w-80 rounded-full bg-[var(--md-error)]/10 blur-3xl" />

      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="mb-2 text-4xl font-normal tracking-tight text-[#1C1B1F]">预测与预警</h1>
          <p className="text-[#49454F]">趋势预测、异常波动监控与策略建议</p>
        </div>
        <MD3Button variant="tonal" icon={<Settings size={18} />}>
          阈值设置
        </MD3Button>
      </div>

      {status.error ? (
        <MD3Card className="border border-[var(--md-error)]/20 bg-[var(--md-error-container)]" hoverable={false}>
          <p className="text-sm text-[var(--md-error)]">预警模块加载失败：{status.error}</p>
        </MD3Card>
      ) : null}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-1">
          <h2 className="px-2 text-xl font-medium text-[#1C1B1F]">当前异常预警 ({alertData.length})</h2>
          {(status.loading ? Array.from({ length: 3 }) : alertData).map((alert, index) =>
            status.loading ? (
              <div key={index} className="h-32 animate-pulse rounded-[24px] bg-[var(--md-surface-container)]" />
            ) : (
              <div
                key={alert.id}
                className={[
                  "overflow-hidden rounded-[24px] border-l-4 bg-[var(--md-surface-container)] p-5 shadow-sm transition-all duration-300 hover:shadow-md",
                  alert.level === "高" ? "border-[var(--md-error)]" : "border-[var(--md-primary)]",
                ].join(" ")}
              >
                <div className="mb-2 flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <MD3Badge color={alert.level === "高" ? "error" : "primary"}>{alert.level}风险</MD3Badge>
                    <span className="font-bold text-[#1C1B1F]">{alert.product}</span>
                  </div>
                  <span className="text-xs text-[#49454F]">{timeAgo(alert.created_at)}</span>
                </div>
                <p className="mb-4 mt-3 text-sm text-[#49454F]">{alert.detail}</p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-[#79747E]">{alert.market}</span>
                  <span className="font-medium text-[#49454F]">
                    当前 {alert.current_value.toFixed(2)} / 阈值 {alert.threshold_value.toFixed(2)}
                  </span>
                </div>
              </div>
            )
          )}
        </div>

        <MD3Card className="flex flex-col xl:col-span-2">
          <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="text-xl font-medium text-[#1C1B1F]">
                {forecast.product}价格 {days} 天预测模型
              </h2>
              <p className="mt-1 text-sm text-[#49454F]">
                算法模型: {forecast.model_name || "趋势预测基线模型"} (MAPE: {forecast.mape}%, RMSE: {forecast.rmse})
              </p>
            </div>
            <div className="flex gap-3 rounded-full bg-[var(--md-surface-container-low)] p-1">
              {forecastDaysOptions.map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setDays(option)}
                  className={[
                    "rounded-full px-4 py-1.5 text-sm font-medium transition-all duration-300",
                    days === option
                      ? "bg-white text-[#1C1B1F] shadow-sm"
                      : "text-[#49454F] hover:bg-black/5",
                  ].join(" ")}
                >
                  {option}天
                </button>
              ))}
            </div>
          </div>

          <div className="chart-panel relative flex-1 rounded-2xl border border-[var(--md-surface-container-low)] bg-white/50 p-6">
            {status.loading ? (
              <div className="mt-8 h-[320px] animate-pulse rounded-2xl bg-[var(--md-surface-container-low)]/70" />
            ) : (
              <>
                <div className="absolute right-4 top-4 flex flex-wrap gap-4 text-xs text-[#49454F]">
                  <div className="flex items-center gap-1">
                    <div className="h-3 w-3 rounded-full bg-[var(--md-primary)]" />
                    实际价格
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="h-3 w-3 rounded-full border-2 border-dashed border-[var(--md-primary)]" />
                    预测中值
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="h-3 w-3 rounded-sm bg-[var(--md-primary-container)]" />
                    置信区间
                  </div>
                </div>
                <svg className="mt-8 h-[320px] w-full" viewBox="0 0 600 280" preserveAspectRatio="none">
                  <path d={buildForecastBand(forecast.history, forecast.forecast, { domain })} fill="#EADDFF" opacity="0.6" />
                  <path d={buildLinePath(forecast.history, { domain })} fill="none" stroke="#6750A4" strokeWidth="3.5" />
                  <path
                    d={buildLinePath([...forecast.history.slice(-1), ...forecast.forecast], { domain })}
                    fill="none"
                    stroke="#6750A4"
                    strokeWidth="3"
                    strokeDasharray="6 6"
                  />
                  {thresholdLine ? (
                    <>
                      <line
                        x1="0"
                        y1={thresholdY}
                        x2="600"
                        y2={thresholdY}
                        stroke="#B3261E"
                        strokeWidth="1"
                        strokeDasharray="4 4"
                        opacity="0.7"
                      />
                      <text x="12" y={Math.max(thresholdY - 6, 12)} fill="#B3261E" fontSize="12">
                        预警线 {thresholdLine.toFixed(2)}
                      </text>
                    </>
                  ) : null}
                  <line x1="315" y1="0" x2="315" y2="280" stroke="#79747E" strokeWidth="1" strokeDasharray="4 4" opacity="0.3" />
                  <text x="282" y="268" fill="#79747E" fontSize="12">
                    今日
                  </text>
                </svg>
              </>
            )}
          </div>

          <div className="mt-6 flex gap-4 rounded-xl bg-[var(--md-secondary-container)]/50 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--md-primary-container)] text-[var(--md-on-primary-container)]">
              <TrendingUp size={20} />
            </div>
            <div>
              <p className="font-medium text-[#1C1B1F]">AI 结论与建议</p>
              <p className="text-sm text-[#49454F]">{forecast.insight || "预测结果加载中..."}</p>
            </div>
          </div>
        </MD3Card>
      </div>
    </div>
  );
}
