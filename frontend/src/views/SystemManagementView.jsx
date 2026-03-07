import { useEffect, useState } from "react";
import { Database, FileText, Server } from "lucide-react";

import { api } from "../api/client";
import EmptyState from "../components/common/EmptyState";
import ErrorState from "../components/common/ErrorState";
import MD3Badge from "../components/ui/MD3Badge";
import MD3Button from "../components/ui/MD3Button";
import MD3Card from "../components/ui/MD3Card";
import MD3Input from "../components/ui/MD3Input";
import { formatDate, timeAgo } from "../utils/formatters";

export default function SystemManagementView() {
  const [taskLogs, setTaskLogs] = useState([]);
  const [rawRecords, setRawRecords] = useState([]);
  const [dataSources, setDataSources] = useState([]);
  const [reportAssets, setReportAssets] = useState([]);
  const [thresholds, setThresholds] = useState([]);
  const [status, setStatus] = useState({ loading: true, error: "" });

  useEffect(() => {
    let active = true;

    async function loadSystemData() {
      setStatus({ loading: true, error: "" });
      try {
        const [taskLogResponse, rawRecordResponse, dataSourceResponse, reportAssetResponse, thresholdResponse] = await Promise.all([
          api.getTaskLogs(10),
          api.getRawRecords(10),
          api.getDataSources(),
          api.getReportAssets(8),
          api.getThresholds(),
        ]);
        if (active) {
          setTaskLogs(taskLogResponse.items);
          setRawRecords(rawRecordResponse.items);
          setDataSources(dataSourceResponse.items);
          setReportAssets(reportAssetResponse.items);
          setThresholds(thresholdResponse.items);
          setStatus({ loading: false, error: "" });
        }
      } catch (error) {
        if (active) {
          setStatus({ loading: false, error: error.message });
        }
      }
    }

    loadSystemData();
    return () => {
      active = false;
    };
  }, []);

  async function handleThresholdSave(item) {
    try {
      const updated = await api.updateThreshold(item.id, {
        warning_ratio: Number(item.warning_ratio),
        critical_ratio: Number(item.critical_ratio),
        std_multiplier: Number(item.std_multiplier),
      });
      setThresholds((current) => current.map((threshold) => (threshold.id === updated.id ? updated : threshold)));
    } catch (error) {
      setStatus((current) => ({ ...current, error: error.message }));
    }
  }

  return (
    <div className="page-enter space-y-8">
      <div>
        <h1 className="mb-2 text-4xl font-normal tracking-tight text-[#1C1B1F]">系统管理</h1>
        <p className="text-[#49454F]">查看真实采集任务日志、原始记录和系统运行基线</p>
      </div>

      {status.error ? (
        <ErrorState title="系统管理数据加载失败" message={status.error} onRetry={() => window.location.reload()} />
      ) : null}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <MD3Card className="xl:col-span-1">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--md-primary-container)] text-[var(--md-on-primary-container)]">
              <Server size={22} />
            </div>
            <div>
              <h2 className="text-xl font-medium text-[#1C1B1F]">采集任务日志</h2>
              <p className="text-sm text-[#49454F]">最近执行的任务状态</p>
            </div>
          </div>
          <div className="space-y-4">
            {(status.loading ? Array.from({ length: 3 }) : taskLogs).map((item, index) =>
              status.loading ? (
                <div key={index} className="h-20 animate-pulse rounded-2xl bg-[var(--md-surface-container-low)]/80" />
              ) : (
                <div key={item.id} className="rounded-2xl bg-white/50 p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <p className="font-medium text-[#1C1B1F]">{item.task_name}</p>
                    <MD3Badge color={item.status === "success" ? "success" : item.status === "failed" ? "error" : "primary"}>
                      {item.status}
                    </MD3Badge>
                  </div>
                  <p className="text-sm text-[#49454F]">{item.message || "暂无说明"}</p>
                  <p className="mt-2 text-xs text-[#79747E]">
                    {timeAgo(item.started_at)} · 写入 {item.records_inserted} 条记录
                  </p>
                </div>
              )
            )}
          </div>
        </MD3Card>

        <MD3Card className="xl:col-span-2">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--md-secondary-container)] text-[var(--md-on-secondary-container)]">
              <Database size={22} />
            </div>
            <div>
              <h2 className="text-xl font-medium text-[#1C1B1F]">原始采集记录</h2>
              <p className="text-sm text-[#49454F]">农业农村部价格简报原始文章入库情况</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-left">
              <thead>
                <tr className="border-b border-[var(--md-surface-container-low)]">
                  <th className="px-4 py-3 text-sm font-medium text-[#49454F]">日期</th>
                  <th className="px-4 py-3 text-sm font-medium text-[#49454F]">标题</th>
                  <th className="px-4 py-3 text-sm font-medium text-[#49454F]">来源</th>
                  <th className="px-4 py-3 text-sm font-medium text-[#49454F]">状态</th>
                </tr>
              </thead>
              <tbody>
                {(status.loading ? Array.from({ length: 5 }) : rawRecords).map((item, index) =>
                  status.loading ? (
                    <tr key={index}>
                      <td className="px-4 py-4" colSpan={4}>
                        <div className="h-10 animate-pulse rounded-xl bg-[var(--md-surface-container-low)]/80" />
                      </td>
                    </tr>
                  ) : (
                    <tr key={item.id} className="border-b border-[var(--md-surface-container-low)]/70">
                      <td className="px-4 py-4 text-sm text-[#1C1B1F]">{item.article_date ? formatDate(item.article_date) : "--"}</td>
                      <td className="px-4 py-4">
                        <div className="flex items-start gap-3">
                          <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-xl bg-[var(--md-primary-container)] text-[var(--md-on-primary-container)]">
                            <FileText size={16} />
                          </div>
                          <div>
                            <p className="font-medium text-[#1C1B1F]">{item.article_title}</p>
                            <a
                              href={item.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-xs text-[var(--md-primary)] hover:underline"
                            >
                              查看原文
                            </a>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-sm text-[#49454F]">{item.source_type}</td>
                      <td className="px-4 py-4">
                        <MD3Badge color={item.status === "success" ? "success" : item.status === "parsed_empty" ? "primary" : "error"}>
                          {item.status}
                        </MD3Badge>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </MD3Card>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <MD3Card>
          <h2 className="text-xl font-medium text-[#1C1B1F]">数据源管理</h2>
          <p className="mt-1 text-sm text-[#49454F]">已批准并接入系统的数据源白名单</p>
          <div className="mt-5 space-y-4">
            {status.loading ? (
              Array.from({ length: 3 }).map((_, index) => <div key={index} className="h-24 animate-pulse rounded-2xl bg-white/50" />)
            ) : dataSources.length ? (
              dataSources.map((item) => (
                <div key={item.id} className="rounded-2xl bg-white/55 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-medium text-[#1C1B1F]">{item.name}</p>
                      <p className="mt-1 text-xs text-[#79747E]">{item.category}</p>
                    </div>
                    <MD3Badge color={item.enabled ? "success" : "neutral"}>{item.enabled ? "启用" : "备用"}</MD3Badge>
                  </div>
                  <a href={item.base_url} target="_blank" rel="noreferrer" className="mt-3 inline-block text-sm text-[var(--md-primary)] hover:underline">
                    {item.base_url}
                  </a>
                  <p className="mt-3 text-sm text-[#49454F]">{item.notes}</p>
                </div>
              ))
            ) : (
              <EmptyState title="暂无数据源" description="后端还没有写入数据源配置。" />
            )}
          </div>
        </MD3Card>

        <MD3Card>
          <h2 className="text-xl font-medium text-[#1C1B1F]">预警阈值配置</h2>
          <p className="mt-1 text-sm text-[#49454F]">可直接调整系统预警比例和标准差阈值</p>
          <div className="mt-5 space-y-4">
            {status.loading ? (
              Array.from({ length: 3 }).map((_, index) => <div key={index} className="h-32 animate-pulse rounded-2xl bg-white/50" />)
            ) : thresholds.length ? (
              thresholds.map((item) => (
                <div key={item.id} className="rounded-2xl bg-white/55 p-4">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <div>
                      <p className="font-medium text-[#1C1B1F]">{item.scope_label}</p>
                      <p className="mt-1 text-xs text-[#79747E]">{item.product_name || "系统默认规则"}</p>
                    </div>
                    <MD3Badge color="primary">更新于 {formatDate(item.updated_at)}</MD3Badge>
                  </div>
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                    <MD3Input
                      label="预警阈值 %"
                      type="number"
                      value={item.warning_ratio}
                      onChange={(event) =>
                        setThresholds((current) =>
                          current.map((threshold) =>
                            threshold.id === item.id ? { ...threshold, warning_ratio: event.target.value } : threshold
                          )
                        )
                      }
                    />
                    <MD3Input
                      label="高危阈值 %"
                      type="number"
                      value={item.critical_ratio}
                      onChange={(event) =>
                        setThresholds((current) =>
                          current.map((threshold) =>
                            threshold.id === item.id ? { ...threshold, critical_ratio: event.target.value } : threshold
                          )
                        )
                      }
                    />
                    <MD3Input
                      label="标准差倍数"
                      type="number"
                      value={item.std_multiplier}
                      onChange={(event) =>
                        setThresholds((current) =>
                          current.map((threshold) =>
                            threshold.id === item.id ? { ...threshold, std_multiplier: event.target.value } : threshold
                          )
                        )
                      }
                    />
                  </div>
                  <div className="mt-4 flex justify-end">
                    <MD3Button variant="outlined" onClick={() => handleThresholdSave(item)}>
                      保存阈值
                    </MD3Button>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState title="暂无阈值配置" description="系统还没有初始化预警阈值数据。" />
            )}
          </div>
        </MD3Card>
      </div>

      <MD3Card>
        <h2 className="text-xl font-medium text-[#1C1B1F]">月报归档</h2>
        <p className="mt-1 text-sm text-[#49454F]">农业农村部农产品供需形势月报归档结果</p>
        <div className="mt-5 space-y-4">
          {status.loading ? (
            Array.from({ length: 3 }).map((_, index) => <div key={index} className="h-24 animate-pulse rounded-2xl bg-white/50" />)
          ) : reportAssets.length ? (
            reportAssets.map((item) => (
              <div key={item.id} className="rounded-2xl bg-white/55 p-4">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <p className="font-medium text-[#1C1B1F]">{item.title}</p>
                    <p className="mt-1 text-xs text-[#79747E]">
                      {item.report_month ? formatDate(item.report_month) : "未识别月份"} · {item.source_type}
                    </p>
                    <p className="mt-3 text-sm text-[#49454F]">{item.summary || "暂无摘要"}</p>
                  </div>
                  <div className="flex flex-col items-start gap-2 md:items-end">
                    <MD3Badge color={item.status === "downloaded" ? "success" : "primary"}>{item.status}</MD3Badge>
                    <a href={item.source_url} target="_blank" rel="noreferrer" className="text-sm text-[var(--md-primary)] hover:underline">
                      查看原始 PDF
                    </a>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <EmptyState title="暂无月报归档" description="请先执行月报同步脚本，将官方 PDF 归档到系统。" />
          )}
        </div>
      </MD3Card>
    </div>
  );
}
