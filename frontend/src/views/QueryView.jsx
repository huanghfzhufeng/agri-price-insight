import { useEffect, useState } from "react";
import { Download, Filter, Search } from "lucide-react";

import { api } from "../api/client";
import EmptyState from "../components/common/EmptyState";
import ErrorState from "../components/common/ErrorState";
import ImageWithFallback from "../components/common/ImageWithFallback";
import MD3Badge from "../components/ui/MD3Badge";
import MD3Button from "../components/ui/MD3Button";
import MD3Card from "../components/ui/MD3Card";
import MD3Input from "../components/ui/MD3Input";
import { resolveProductImage } from "../data/productImageManifest";
import { formatDate, formatPrice } from "../utils/formatters";

const defaultFilters = {
  product: "",
  market: "",
  category: "",
  start_date: "",
  end_date: "",
  page: 1,
  page_size: 12,
};

export default function QueryView() {
  const [filters, setFilters] = useState(defaultFilters);
  const [options, setOptions] = useState({ products: [], markets: [], categories: [] });
  const [prices, setPrices] = useState({ items: [], total: 0 });
  const [status, setStatus] = useState({ loading: true, error: "" });

  useEffect(() => {
    let active = true;

    async function loadInitialData() {
      setStatus({ loading: true, error: "" });
      try {
        const [systemOptions, priceData] = await Promise.all([api.getSystemOptions(), api.getPrices(defaultFilters)]);
        if (active) {
          setOptions(systemOptions);
          setPrices(priceData);
          setStatus({ loading: false, error: "" });
        }
      } catch (error) {
        if (active) {
          setStatus({ loading: false, error: error.message });
        }
      }
    }

    loadInitialData();
    return () => {
      active = false;
    };
  }, []);

  async function runSearch(nextFilters = filters) {
    setStatus({ loading: true, error: "" });
    try {
      const data = await api.getPrices(nextFilters);
      setPrices(data);
      setStatus({ loading: false, error: "" });
    } catch (error) {
      setStatus({ loading: false, error: error.message });
    }
  }

  function updateFilter(field, value) {
    setFilters((current) => ({ ...current, [field]: value, page: field === "page" ? value : 1 }));
  }

  async function handleExport() {
    try {
      await api.downloadPrices(filters);
    } catch (error) {
      setStatus({ loading: false, error: error.message });
    }
  }

  return (
    <div className="page-enter relative space-y-8">
      <div className="pointer-events-none absolute left-1/2 top-0 -z-10 h-64 w-full -translate-x-1/2 rounded-full bg-[var(--md-secondary-container)]/40 blur-3xl" />

      <div>
        <h1 className="mb-2 text-4xl font-normal tracking-tight text-[#1C1B1F]">数据查询</h1>
        <p className="text-[#49454F]">多维度农产品价格检索与对比</p>
      </div>

      <div className="rounded-[32px] bg-[var(--md-surface-container)] p-8 shadow-sm">
        <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-4">
          <MD3Input
            label="输入农产品名称"
            placeholder="如：苹果"
            icon={Search}
            value={filters.product}
            onChange={(event) => updateFilter("product", event.target.value)}
            list="product-options"
          />
          <MD3Input
            label="选择地区/市场"
            placeholder="如：北京新发地"
            value={filters.market}
            onChange={(event) => updateFilter("market", event.target.value)}
            list="market-options"
          />
          <MD3Input
            label="开始日期"
            type="date"
            value={filters.start_date}
            onChange={(event) => updateFilter("start_date", event.target.value)}
          />
          <MD3Input
            label="结束日期"
            type="date"
            value={filters.end_date}
            onChange={(event) => updateFilter("end_date", event.target.value)}
          />
        </div>

        <datalist id="product-options">
          {options.products.map((product) => (
            <option key={product} value={product} />
          ))}
        </datalist>

        <datalist id="market-options">
          {options.markets.map((market) => (
            <option key={market} value={market} />
          ))}
        </datalist>

        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap gap-2">
            {options.categories.map((category) => (
              <MD3Badge
                key={category}
                active={filters.category === category}
                onClick={() => {
                  const nextCategory = filters.category === category ? "" : category;
                  const nextFilters = { ...filters, category: nextCategory };
                  setFilters(nextFilters);
                  runSearch(nextFilters);
                }}
              >
                {category}
              </MD3Badge>
            ))}
          </div>
          <div className="flex gap-3">
            <MD3Button
              variant="tonal"
              icon={<Filter size={18} />}
              onClick={() => {
                setFilters(defaultFilters);
                runSearch(defaultFilters);
              }}
            >
              重置筛选
            </MD3Button>
            <MD3Button variant="outlined" icon={<Download size={18} />} onClick={handleExport}>
              导出 CSV
            </MD3Button>
            <MD3Button icon={<Search size={18} />} onClick={() => runSearch()}>
              立即查询
            </MD3Button>
          </div>
        </div>
      </div>

      {status.error ? (
        <ErrorState title="查询失败" message={status.error} onRetry={() => runSearch()} />
      ) : null}

      <MD3Card>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-medium text-[#1C1B1F]">价格明细</h2>
            <p className="mt-1 text-sm text-[#49454F]">
              当前匹配到 {prices.total} 条记录，第 {prices.page || 1} / {prices.pages || 1} 页
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] border-collapse text-left">
            <thead>
              <tr className="border-b-2 border-[var(--md-surface-container-low)]">
                <th className="px-4 py-4 text-sm font-medium text-[#49454F]">日期</th>
                <th className="px-4 py-4 text-sm font-medium text-[#49454F]">品名</th>
                <th className="px-4 py-4 text-sm font-medium text-[#49454F]">分类</th>
                <th className="px-4 py-4 text-sm font-medium text-[#49454F]">市场/地区</th>
                <th className="px-4 py-4 text-sm font-medium text-[#49454F]">均价</th>
                <th className="px-4 py-4 text-sm font-medium text-[#49454F]">环比涨跌</th>
                <th className="px-4 py-4 text-sm font-medium text-[#49454F]">数据来源</th>
              </tr>
            </thead>
            <tbody>
              {status.loading ? (
                Array.from({ length: 5 }).map((_, index) => (
                  <tr key={index} className="border-b border-[var(--md-surface-container-low)]">
                    <td className="px-4 py-4" colSpan={7}>
                      <div className="h-10 animate-pulse rounded-xl bg-[var(--md-surface-container-low)]/80" />
                    </td>
                  </tr>
                ))
              ) : prices.items.length ? (
                prices.items.map((item) => (
                  <tr
                    key={item.id}
                    className="group border-b border-[var(--md-surface-container-low)] transition-colors hover:bg-[var(--md-secondary-container)]/30"
                  >
                    <td className="px-4 py-4 text-[#1C1B1F]">{formatDate(item.stat_date)}</td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-3">
                        <ImageWithFallback
                          src={resolveProductImage(item.product_name).src}
                          alt={resolveProductImage(item.product_name).alt}
                          className="h-12 w-12 rounded-2xl object-cover shadow-sm"
                          loading="lazy"
                        />
                        <div>
                          <p className="font-medium text-[#1C1B1F]">{item.product_name}</p>
                          <p className="text-xs text-[#79747E]">{resolveProductImage(item.product_name).displayName}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-[#49454F]">{item.category}</td>
                    <td className="px-4 py-4 text-[#49454F]">
                      {item.market_name}
                      <span className="ml-2 text-xs text-[#79747E]">{item.region}</span>
                    </td>
                    <td className="px-4 py-4 font-medium">{formatPrice(item.avg_price, item.unit)}</td>
                    <td
                      className={[
                        "px-4 py-4 font-medium",
                        item.change_rate >= 0 ? "text-[var(--md-success)]" : "text-[var(--md-error)]",
                      ].join(" ")}
                    >
                      {item.change_rate >= 0 ? "+" : ""}
                      {item.change_rate.toFixed(1)}%
                    </td>
                    <td className="px-4 py-4 text-sm text-[#49454F]">{item.source}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-sm text-[#49454F]">
                    <EmptyState title="暂无符合条件的数据" description="调整筛选条件后重新查询。" className="mx-auto max-w-xl" />
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-6 flex flex-col gap-4 border-t border-[var(--md-surface-container-low)] pt-5 md:flex-row md:items-center md:justify-between">
          <p className="text-sm text-[#49454F]">每页显示 {filters.page_size} 条</p>
          <div className="flex items-center gap-3">
            <MD3Button
              variant="outlined"
              onClick={() => {
                if ((prices.page || 1) <= 1) {
                  return;
                }
                const nextFilters = { ...filters, page: (prices.page || 1) - 1 };
                setFilters(nextFilters);
                runSearch(nextFilters);
              }}
            >
              上一页
            </MD3Button>
            <span className="text-sm text-[#49454F]">
              {prices.page || 1} / {prices.pages || 1}
            </span>
            <MD3Button
              variant="outlined"
              onClick={() => {
                if ((prices.page || 1) >= (prices.pages || 1)) {
                  return;
                }
                const nextFilters = { ...filters, page: (prices.page || 1) + 1 };
                setFilters(nextFilters);
                runSearch(nextFilters);
              }}
            >
              下一页
            </MD3Button>
          </div>
        </div>
      </MD3Card>
    </div>
  );
}
