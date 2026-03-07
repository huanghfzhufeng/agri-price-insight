import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import { RefreshCcw } from "lucide-react";

import { api } from "../api/client";
import EmptyState from "../components/common/EmptyState";
import ErrorState from "../components/common/ErrorState";
import MD3Button from "../components/ui/MD3Button";
import MD3Card from "../components/ui/MD3Card";
import MD3Input from "../components/ui/MD3Input";
import { formatDate } from "../utils/formatters";

const defaultFilters = {
  product: "大蒜",
  market: "全国均价",
};

function buildTrendOption(trend) {
  const dates = trend.series[0]?.points.map((point) => point.date) || [];
  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0, textStyle: { color: "#49454F" } },
    grid: { left: 30, right: 20, top: 44, bottom: 30, containLabel: true },
    xAxis: {
      type: "category",
      data: dates,
      boundaryGap: false,
      axisLabel: { color: "#79747E" },
      axisLine: { lineStyle: { color: "#D6CEDA" } },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#79747E" },
      splitLine: { lineStyle: { color: "rgba(121,116,126,0.12)" } },
    },
    series: trend.series.map((series, index) => ({
      name: series.name,
      type: "line",
      smooth: true,
      symbol: "none",
      data: series.points.map((point) => point.value),
      lineStyle: { width: 3 },
      areaStyle: index === 0 ? { color: "rgba(103,80,164,0.12)" } : undefined,
    })),
    color: ["#6750A4", "#386A20", "#B3261E", "#2F6A7D"],
  };
}

function buildMonthlyOption(monthly) {
  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0, textStyle: { color: "#49454F" } },
    grid: { left: 30, right: 24, top: 44, bottom: 30, containLabel: true },
    xAxis: {
      type: "category",
      data: monthly.points.map((point) => point.month),
      axisLabel: { color: "#79747E", rotate: 30 },
      axisLine: { lineStyle: { color: "#D6CEDA" } },
    },
    yAxis: [
      {
        type: "value",
        name: "均价",
        axisLabel: { color: "#79747E" },
        splitLine: { lineStyle: { color: "rgba(121,116,126,0.12)" } },
      },
      {
        type: "value",
        name: "涨跌幅 %",
        axisLabel: { color: "#79747E" },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "本期均价",
        type: "bar",
        barMaxWidth: 26,
        data: monthly.points.map((point) => point.current_avg),
        itemStyle: { borderRadius: [10, 10, 0, 0], color: "#6750A4" },
      },
      {
        name: "环比",
        type: "line",
        yAxisIndex: 1,
        smooth: true,
        symbolSize: 7,
        data: monthly.points.map((point) => point.mom_change),
        itemStyle: { color: "#386A20" },
        lineStyle: { width: 3, color: "#386A20" },
      },
      {
        name: "同比",
        type: "line",
        yAxisIndex: 1,
        smooth: true,
        symbolSize: 7,
        data: monthly.points.map((point) => point.yoy_change),
        itemStyle: { color: "#B3261E" },
        lineStyle: { width: 3, color: "#B3261E", type: "dashed" },
      },
    ],
  };
}

function buildRegionOption(regionData) {
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 30, right: 20, top: 24, bottom: 30, containLabel: true },
    xAxis: {
      type: "category",
      data: regionData.items.map((item) => item.market),
      axisLabel: { color: "#79747E", rotate: 18 },
      axisLine: { lineStyle: { color: "#D6CEDA" } },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#79747E" },
      splitLine: { lineStyle: { color: "rgba(121,116,126,0.12)" } },
    },
    series: [
      {
        type: "bar",
        data: regionData.items.map((item) => item.value),
        barMaxWidth: 34,
        itemStyle: {
          borderRadius: [10, 10, 0, 0],
          color: "#7D5260",
        },
      },
    ],
  };
}

export default function AnalysisView() {
  const [filters, setFilters] = useState(defaultFilters);
  const [options, setOptions] = useState({ products: [], markets: [] });
  const [overview, setOverview] = useState({ product: "", market: "", latest_date: null, metrics: [] });
  const [trend, setTrend] = useState({ series: [] });
  const [monthly, setMonthly] = useState({ points: [] });
  const [regions, setRegions] = useState({ items: [] });
  const [volatility, setVolatility] = useState({ items: [] });
  const [anomalies, setAnomalies] = useState({ items: [] });
  const [status, setStatus] = useState({ loading: true, error: "" });

  useEffect(() => {
    let active = true;

    async function loadOptions() {
      const systemOptions = await api.getSystemOptions();
      if (!active) {
        return;
      }
      setOptions(systemOptions);
      const nextFilters = {
        product: systemOptions.products.includes(defaultFilters.product) ? defaultFilters.product : systemOptions.products[0] || "",
        market: systemOptions.markets.includes(defaultFilters.market) ? defaultFilters.market : systemOptions.markets[0] || "",
      };
      setFilters(nextFilters);
    }

    loadOptions().catch((error) => {
      if (active) {
        setStatus({ loading: false, error: error.message });
      }
    });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!filters.product || !filters.market) {
      return;
    }
    let active = true;

    async function loadAnalysisData() {
      setStatus({ loading: true, error: "" });
      try {
        const [overviewData, trendData, monthlyData, regionData, volatilityData, anomalyData] = await Promise.all([
          api.getAnalysisOverview(filters.product, filters.market),
          api.getAnalysisTrend(filters.product, 90),
          api.getAnalysisMonthly(filters.product, filters.market),
          api.getAnalysisRegions(filters.product),
          api.getAnalysisVolatility(30),
          api.getAnalysisAnomalies(filters.product, filters.market, 120),
        ]);

        if (!active) {
          return;
        }

        setOverview(overviewData);
        setTrend(trendData);
        setMonthly(monthlyData);
        setRegions(regionData);
        setVolatility(volatilityData);
        setAnomalies(anomalyData);
        setStatus({ loading: false, error: "" });
      } catch (error) {
        if (active) {
          setStatus({ loading: false, error: error.message });
        }
      }
    }

    loadAnalysisData();
    return () => {
      active = false;
    };
  }, [filters.product, filters.market]);

  return (
    <div className="page-enter space-y-8">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <h1 className="mb-2 text-4xl font-normal tracking-tight text-[#1C1B1F]">统计分析</h1>
          <p className="text-[#49454F]">同比环比、区域比较、波动率与异常值分析</p>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <MD3Input
            label="选择农产品"
            value={filters.product}
            onChange={(event) => setFilters((current) => ({ ...current, product: event.target.value }))}
            list="analysis-products"
          />
          <MD3Input
            label="选择市场"
            value={filters.market}
            onChange={(event) => setFilters((current) => ({ ...current, market: event.target.value }))}
            list="analysis-markets"
          />
          <datalist id="analysis-products">
            {options.products.map((product) => (
              <option key={product} value={product} />
            ))}
          </datalist>
          <datalist id="analysis-markets">
            {options.markets.map((market) => (
              <option key={market} value={market} />
            ))}
          </datalist>
        </div>
      </div>

      {status.error ? (
        <ErrorState title="统计分析加载失败" message={status.error} onRetry={() => setFilters((current) => ({ ...current }))} />
      ) : null}

      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
        {(status.loading ? Array.from({ length: 6 }) : overview.metrics).map((metric, index) => (
          <MD3Card key={metric?.title || index}>
            {status.loading ? (
              <div className="space-y-4 animate-pulse">
                <div className="h-4 w-24 rounded-full bg-white/60" />
                <div className="h-10 w-28 rounded-full bg-white/70" />
                <div className="h-4 w-20 rounded-full bg-white/60" />
              </div>
            ) : (
              <>
                <p className="text-sm font-medium text-[#49454F]">{metric.title}</p>
                <div className="mt-4 flex items-end gap-2">
                  <span className="text-4xl font-semibold text-[#1C1B1F]">{metric.value.toFixed(metric.unit === "个" ? 0 : 2)}</span>
                  <span className="pb-1 text-sm text-[#79747E]">{metric.unit}</span>
                </div>
                <p className="mt-4 text-sm text-[#49454F]">
                  {metric.change_label}
                  {metric.change !== null && metric.change !== undefined ? ` ${metric.change >= 0 ? "+" : ""}${metric.change.toFixed(2)}%` : ""}
                </p>
              </>
            )}
          </MD3Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <MD3Card className="xl:col-span-2">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-medium text-[#1C1B1F]">近 90 天市场趋势对比</h2>
              <p className="mt-1 text-sm text-[#49454F]">{overview.product || filters.product} 各市场价格变化</p>
            </div>
            <MD3Button variant="text" icon={<RefreshCcw size={18} />} onClick={() => setFilters((current) => ({ ...current }))}>
              刷新
            </MD3Button>
          </div>
          {status.loading ? (
            <div className="h-[360px] animate-pulse rounded-[24px] bg-white/50" />
          ) : trend.series.length ? (
            <ReactECharts option={buildTrendOption(trend)} style={{ height: 360 }} />
          ) : (
            <EmptyState title="暂无趋势数据" description="当前筛选条件下没有可绘制的市场趋势。" className="h-[360px]" />
          )}
        </MD3Card>

        <MD3Card>
          <h2 className="text-2xl font-medium text-[#1C1B1F]">异常值监测</h2>
          <p className="mt-1 text-sm text-[#49454F]">
            {overview.market || filters.market}
            {overview.latest_date ? ` · 最新数据 ${formatDate(overview.latest_date)}` : ""}
          </p>
          <div className="mt-5 space-y-3">
            {status.loading ? (
              Array.from({ length: 5 }).map((_, index) => <div key={index} className="h-16 animate-pulse rounded-2xl bg-white/50" />)
            ) : anomalies.items.length ? (
              anomalies.items.slice(0, 5).map((item) => (
                <div key={item.date} className="rounded-2xl bg-white/55 p-4">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-[#1C1B1F]">{formatDate(item.date)}</p>
                    <span className={item.severity === "高" ? "text-[var(--md-error)]" : "text-[var(--md-primary)]"}>{item.severity}风险</span>
                  </div>
                  <p className="mt-2 text-sm text-[#49454F]">
                    实际值 {item.value.toFixed(2)}，IQR 区间 {item.lower_bound.toFixed(2)} - {item.upper_bound.toFixed(2)}
                  </p>
                </div>
              ))
            ) : (
              <EmptyState title="未发现异常值" description="当前窗口内价格波动仍处于正常区间。" />
            )}
          </div>
        </MD3Card>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <MD3Card className="xl:col-span-2">
          <h2 className="text-2xl font-medium text-[#1C1B1F]">同比与环比</h2>
          <p className="mt-1 text-sm text-[#49454F]">近 12 个月月均价、同比和环比变化</p>
          {status.loading ? (
            <div className="mt-5 h-[340px] animate-pulse rounded-[24px] bg-white/50" />
          ) : monthly.points.length ? (
            <ReactECharts option={buildMonthlyOption(monthly)} style={{ height: 340, marginTop: 20 }} />
          ) : (
            <EmptyState title="暂无月度数据" description="请先完成历史数据同步后再查看同比环比趋势。" className="mt-5 h-[340px]" />
          )}
        </MD3Card>

        <MD3Card>
          <h2 className="text-2xl font-medium text-[#1C1B1F]">波动率排行</h2>
          <p className="mt-1 text-sm text-[#49454F]">近 30 天波动最明显的产品与市场组合</p>
          <div className="mt-5 space-y-3">
            {status.loading ? (
              Array.from({ length: 5 }).map((_, index) => <div key={index} className="h-16 animate-pulse rounded-2xl bg-white/50" />)
            ) : (
              volatility.items.slice(0, 5).map((item) => (
                <div key={`${item.product}-${item.market}`} className="rounded-2xl bg-white/55 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-[#1C1B1F]">{item.product}</p>
                      <p className="mt-1 text-xs text-[#79747E]">{item.market}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-[#1C1B1F]">{item.volatility.toFixed(2)}%</p>
                      <p className="text-xs text-[#79747E]">振幅 {item.range_ratio.toFixed(2)}%</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </MD3Card>
      </div>

      <MD3Card>
        <div className="mb-5">
          <h2 className="text-2xl font-medium text-[#1C1B1F]">区域对比</h2>
          <p className="mt-1 text-sm text-[#49454F]">{filters.product} 最新市场价格对比</p>
        </div>
        {status.loading ? (
          <div className="h-[320px] animate-pulse rounded-[24px] bg-white/50" />
        ) : regions.items.length ? (
          <ReactECharts option={buildRegionOption(regions)} style={{ height: 320 }} />
        ) : (
          <EmptyState title="暂无区域对比数据" description="当前所选农产品没有市场横向对比数据。" className="h-[320px]" />
        )}
      </MD3Card>
    </div>
  );
}
