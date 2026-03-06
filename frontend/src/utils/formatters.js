export function formatNumber(value) {
  return new Intl.NumberFormat("zh-CN").format(value);
}

export function formatPrice(value, unit) {
  const normalizedUnit = unit.startsWith("元/") ? unit.slice(2) : unit;
  return `¥ ${Number(value).toFixed(2)} / ${normalizedUnit}`;
}

export function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

export function timeAgo(dateString) {
  const now = Date.now();
  const target = new Date(dateString).getTime();
  const diffMinutes = Math.max(Math.round((now - target) / 60000), 0);

  if (diffMinutes < 60) {
    return `${diffMinutes || 1} 分钟前`;
  }

  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) {
    return `${diffHours} 小时前`;
  }

  const diffDays = Math.round(diffHours / 24);
  return `${diffDays} 天前`;
}
