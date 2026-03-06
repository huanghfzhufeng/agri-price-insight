function resolveDomain(points, domain) {
  if (domain) {
    return domain;
  }

  const values = points.flatMap((point) => [point.lower_bound ?? point.value, point.upper_bound ?? point.value]);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  return { minValue, maxValue };
}

export function getValueDomain(seriesCollection) {
  const points = seriesCollection.flat();
  if (!points.length) {
    return { minValue: 0, maxValue: 1 };
  }

  return resolveDomain(points);
}

export function getYCoordinate(value, domain, height = 280, padding = 24) {
  const valueRange = domain.maxValue - domain.minValue || 1;
  const ratio = (value - domain.minValue) / valueRange;
  return height - padding - ratio * (height - padding * 2);
}

export function buildLinePath(points, options = {}) {
  const { width = 600, height = 280, padding = 24, domain } = options;
  if (!points.length) {
    return "";
  }

  const { minValue, maxValue } = resolveDomain(points, domain);
  const valueRange = maxValue - minValue || 1;
  const stepX = points.length > 1 ? (width - padding * 2) / (points.length - 1) : 0;

  return points
    .map((point, index) => {
      const x = padding + stepX * index;
      const ratio = (point.value - minValue) / valueRange;
      const y = height - padding - ratio * (height - padding * 2);
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

export function buildAreaPath(points, options = {}) {
  const { width = 600, height = 280, padding = 24, domain } = options;
  if (!points.length) {
    return "";
  }

  const linePath = buildLinePath(points, { width, height, padding, domain });
  const lastX = width - padding;
  const firstX = padding;
  const baseline = height - padding;
  return `${linePath} L ${lastX} ${baseline} L ${firstX} ${baseline} Z`;
}

export function buildForecastBand(history, forecast, options = {}) {
  const { width = 600, height = 280, padding = 24, domain } = options;
  const merged = [...history, ...forecast];
  if (!forecast.length || !merged.length) {
    return "";
  }

  const { minValue, maxValue } = resolveDomain(merged, domain);
  const valueRange = maxValue - minValue || 1;
  const stepX = merged.length > 1 ? (width - padding * 2) / (merged.length - 1) : 0;

  const upperPath = forecast
    .map((point, index) => {
      const absoluteIndex = history.length + index;
      const x = padding + stepX * absoluteIndex;
      const ratio = ((point.upper_bound ?? point.value) - minValue) / valueRange;
      const y = height - padding - ratio * (height - padding * 2);
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");

  const lowerPath = [...forecast]
    .reverse()
    .map((point, index) => {
      const absoluteIndex = history.length + forecast.length - 1 - index;
      const x = padding + stepX * absoluteIndex;
      const ratio = ((point.lower_bound ?? point.value) - minValue) / valueRange;
      const y = height - padding - ratio * (height - padding * 2);
      return `L ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");

  return `${upperPath} ${lowerPath} Z`;
}
