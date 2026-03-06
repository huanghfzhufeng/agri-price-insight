import { useEffect, useState } from "react";
import { Database, FileText, Server } from "lucide-react";

import { api } from "../api/client";
import MD3Badge from "../components/ui/MD3Badge";
import MD3Card from "../components/ui/MD3Card";
import { formatDate, timeAgo } from "../utils/formatters";

export default function SystemManagementView() {
  const [taskLogs, setTaskLogs] = useState([]);
  const [rawRecords, setRawRecords] = useState([]);
  const [status, setStatus] = useState({ loading: true, error: "" });

  useEffect(() => {
    let active = true;

    async function loadSystemData() {
      setStatus({ loading: true, error: "" });
      try {
        const [taskLogResponse, rawRecordResponse] = await Promise.all([api.getTaskLogs(10), api.getRawRecords(10)]);
        if (active) {
          setTaskLogs(taskLogResponse.items);
          setRawRecords(rawRecordResponse.items);
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

  return (
    <div className="page-enter space-y-8">
      <div>
        <h1 className="mb-2 text-4xl font-normal tracking-tight text-[#1C1B1F]">系统管理</h1>
        <p className="text-[#49454F]">查看真实采集任务日志、原始记录和系统运行基线</p>
      </div>

      {status.error ? (
        <MD3Card className="border border-[var(--md-error)]/20 bg-[var(--md-error-container)]" hoverable={false}>
          <p className="text-sm text-[var(--md-error)]">系统管理数据加载失败：{status.error}</p>
        </MD3Card>
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
    </div>
  );
}
