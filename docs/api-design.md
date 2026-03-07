# 接口设计文档

## 1. 认证接口

### `POST /api/v1/auth/login`

用途：管理员登录。

请求体：

```json
{
  "username": "admin",
  "password": "Admin@123456"
}
```

### `GET /api/v1/auth/me`

用途：获取当前登录用户信息。

### `POST /api/v1/auth/logout`

用途：退出登录并销毁令牌。

## 2. 系统接口

### `GET /api/v1/system/health`

用途：健康检查。

### `GET /api/v1/system/options`

用途：获取产品、市场、分类选项。

### `GET /api/v1/system/task-logs`

用途：查询采集任务日志。

### `GET /api/v1/system/raw-records`

用途：查询原始文章记录。

### `GET /api/v1/system/data-sources`

用途：查询数据源白名单。

### `GET /api/v1/system/report-assets`

用途：查询月报归档。

### `GET /api/v1/system/thresholds`

用途：查询预警阈值配置。

### `PUT /api/v1/system/thresholds/{threshold_id}`

用途：更新预警阈值。

## 3. 仪表盘接口

### `GET /api/v1/dashboard`

用途：获取概览指标、趋势数据和涨跌排行。

### `GET /api/v1/dashboard/rankings`

用途：获取涨跌排行。

## 4. 数据查询接口

### `GET /api/v1/prices`

用途：分页查询价格明细。

关键参数：

- `product`
- `market`
- `category`
- `start_date`
- `end_date`
- `page`
- `page_size`

### `GET /api/v1/prices/export`

用途：导出 CSV 报表。

## 5. 统计分析接口

### `GET /api/v1/analysis/overview`

用途：获取统计分析 KPI。

### `GET /api/v1/analysis/trend`

用途：获取多市场趋势线。

### `GET /api/v1/analysis/monthly`

用途：获取同比环比所需月度聚合数据。

### `GET /api/v1/analysis/regions`

用途：获取区域对比条形图数据。

### `GET /api/v1/analysis/volatility`

用途：获取波动率排行。

### `GET /api/v1/analysis/anomalies`

用途：获取 IQR 异常值识别结果。

## 6. 预测预警接口

### `GET /api/v1/alerts`

用途：获取当前预警列表。

### `GET /api/v1/alerts/forecast`

用途：获取价格预测、置信区间和模型评价指标。

关键参数：

- `product`
- `days`
- `model`

## 7. 鉴权规则

- `system/health` 与 `auth/login` 为公开接口。
- 其余业务接口均要求 `Authorization: Bearer <token>`。
