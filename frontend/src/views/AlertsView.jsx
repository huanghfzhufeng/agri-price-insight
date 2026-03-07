import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import { Settings, TrendingUp } from "lucide-react";

import { api } from "../api/client";
import EmptyState from "../components/common/EmptyState";
import ErrorState from "../components/common/ErrorState";
import ImageWithFallback from "../components/common/ImageWithFallback";
import MD3Badge from "../components/ui/MD3Badge";
import MD3Button from "../components/ui/MD3Button";
import MD3Card from "../components/ui/MD3Card";
import { resolveProductImage } from "../data/productImageManifest";
import { timeAgo } from "../utils/formatters";

const forecastDaysOptions = [7, 30, 90];

function buildForecastOption(forecast) {
  const labels = [...forecast.history.map((item) => item.date), ...forecast.forecast.map((item) => item.date)];
  const actualSeries = [...forecast.history.map((item) => item.value), ...forecast.forecast.map(() => null)];
  const lowerSeries = [...forecast.history.map(() => null), ...forecast.forecast.map((item) => item.lower_bound)];
  const bandSeries = [...forecast.history.map(() => null), ...forecast.forecast.map((item) => (item.upper_bound ?? item.value) - (item.lower_bound ?? item.value))];
  const forecastSeries = [
    ...forecast.history.map(() => null),
    ...forecast.forecast.map((item) => item.value),
  ];
  const maxThreshold = forecast.forecast.reduce((result, item) => Math.max(result, item.upper_bound ?? item.value), 0);

  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0, textStyle: { color: "#49454F" } },
    grid: { left: 30, right: 20, top: 44, bottom: 30, containLabel: true },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: labels,
      axisLabel: { color: "#79747E", hideOverlap: true },
      axisLine: { lineStyle: { color: "#D6CEDA" } },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#79747E" },
      splitLine: { lineStyle: { color: "rgba(121,116,126,0.12)" } },
    },
    series: [
      {
        name: "置信区间下轨",
        type: "line",
        stack: "band",
        symbol: "none",
        lineStyle: { opacity: 0 },
        areaStyle: { opacity: 0 },
        data: lowerSeries,
      },
      {
        name: "置信区间",
        type: "line",
        stack: "band",
        symbol: "none",
        lineStyle: { opacity: 0 },
        areaStyle: { color: "rgba(103,80,164,0.18)" },
        data: bandSeries,
      },
      {
        name: "实际价格",
        type: "line",
        symbol: "none",
        smooth: true,
        data: actualSeries,
        lineStyle: { width: 3.5, color: "#6750A4" },
      },
      {
        name: "预测价格",
        type: "line",
        symbol: "none",
        smooth: true,
        data: forecastSeries,
        lineStyle: { width: 3, type: "dashed", color: "#386A20" },
        markLine: {
          symbol: "none",
          data: [{ yAxis: Number(maxThreshold.toFixed(2)), name: "预警线" }],
          lineStyle: { color: "#B3261E", type: "dashed" },
          label: { color: "#B3261E" },
        },
      },
    ],
  };
}

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

  const forecastImage = resolveProductImage(forecast.product);

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

      {status.error ? <ErrorState title="预测预警加载失败" message={status.error} onRetry={() => setDays((current) => current)} /> : null}

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
                  <div className="flex items-center gap-3">
                    <ImageWithFallback
                      src={resolveProductImage(alert.product).src}
                      alt={resolveProductImage(alert.product).alt}
                      className="h-12 w-12 rounded-2xl object-cover shadow-sm"
                      loading="lazy"
                    />
                    <div className="flex items-center gap-2">
                      <MD3Badge color={alert.level === "高" ? "error" : "primary"}>{alert.level}风险</MD3Badge>
                      <span className="font-bold text-[#1C1B1F]">{alert.product}</span>
                    </div>
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
            <div className="flex items-center gap-4">
              <ImageWithFallback
                src={forecastImage.src}
                alt={forecastImage.alt}
                className="h-16 w-16 rounded-[20px] object-cover shadow-sm"
                loading="lazy"
              />
              <div>
                <h2 className="text-xl font-medium text-[#1C1B1F]">
                  {forecast.product}价格 {days} 天预测模型
                </h2>
                <p className="mt-1 text-sm text-[#49454F]">
                  算法模型: {forecast.model_name || "趋势预测基线模型"} (MAPE: {forecast.mape}%, RMSE: {forecast.rmse}, MAE:{" "}
                  {forecast.mae ?? 0})
                </p>
              </div>
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
            ) : !forecast.forecast.length ? (
              <EmptyState title="暂无预测结果" description="当前数据量不足，暂时无法生成未来走势。" className="mt-8 h-[320px]" />
            ) : (
              <>
                <ReactECharts option={buildForecastOption(forecast)} style={{ height: 360, marginTop: 20 }} />
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
              <div className="mt-3 flex flex-wrap gap-2">
                {(forecast.available_models || []).map((item) => (
                  <MD3Badge
                    key={item.key || item.model_name}
                    color={item.available === false ? "neutral" : item.model_name === forecast.model_name ? "primary" : "success"}
                  >
                    {item.model_name}
                    {item.available === false ? " 不可用" : item.mape !== null && item.mape !== undefined ? ` · MAPE ${item.mape}%` : ""}
                  </MD3Badge>
                ))}
              </div>
              {forecastImage.sourcePage ? (
                <a
                  href={forecastImage.sourcePage}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-2 inline-block text-xs text-[var(--md-primary)] hover:underline"
                >
                  查看图片来源
                </a>
              ) : null}
            </div>
          </div>
        </MD3Card>
      </div>

    </div>
  );
}
