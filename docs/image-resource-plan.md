# 图片资源方案

## 1. 文档目的

本文档用于明确本项目中农产品图片资源的获取方式、授权约束、存储方式和前端展示方案。

你的要求是：

- 真实数据要尽量配合图片展示
- 图片要能在前端页面中稳定显示
- 图片来源要可说明、可审查

因此本项目采用“价格数据与图片资源分层”的方案。

## 2. 核心原则

- 价格数据和图片数据分开获取
- 价格数据优先走官方源
- 图片资源优先走可公开使用的来源
- 图片最终本地化存储，避免前端直接依赖第三方外链
- 每张图片必须保留来源页、作者和许可信息

## 3. 不采用的方案

以下方案不建议作为正式毕业设计实现：

- 直接从百度图片或搜索引擎结果页抓图
- 直接使用来源不明的商品主图
- 在前端直接引用不稳定的外链图片
- 从价格新闻页中强行抽取不规范配图作为产品主图

原因：

- 容易有版权问题
- 容易失效
- 无法在论文或答辩中说明来源合法性

## 4. 推荐图片来源

### 4.1 方案 A：Wikimedia Commons

许可说明：

- [Commons:Licensing](https://commons.wikimedia.org/wiki/Commons:Licensing)

说明：

- Wikimedia Commons 仅接受允许再发布、允许演绎、允许商业使用的自由许可内容
- 但具体使用时，仍然需要检查每一张图片页面上的单独授权信息和署名要求

推荐用途：

- 用于系统演示版和毕业设计展示版图片库
- 为重点农产品构建首批本地素材

### 4.2 方案 B：自行拍摄或自有素材

说明：

- 如果你可以自己拍摄农产品图片，这是最终最稳妥的方式
- 完全避免第三方版权问题
- 特别适合论文提交和答辩展示

推荐用途：

- 用于替换首批演示图片
- 作为最终提交版默认素材

## 5. 推荐图片来源页

以下链接是我建议优先审查和使用的图片来源页入口。

### 大蒜

- [Category:Garlic](https://commons.wikimedia.org/wiki/Category:Garlic)
- [Category:Garlics as food](https://commons.wikimedia.org/wiki/Category:Garlics_as_food)

### 大白菜

- [Category:Napa cabbage](https://commons.wikimedia.org/wiki/Category:Napa_cabbage)
- [Category:Brassica rapa subsp. pekinensis](https://commons.wikimedia.org/wiki/Category:Brassica_rapa_subsp._pekinensis)

### 鸡蛋

- [Category:Eggs as food](https://commons.wikimedia.org/wiki/Category:Eggs_as_food)
- [Category:Raw eggs](https://commons.wikimedia.org/wiki/Category:Raw_eggs)

### 苹果

- [Category:Apples](https://commons.wikimedia.org/wiki/Category:Apples)
- [Category:1 apple](https://commons.wikimedia.org/wiki/Category:1_apple)

### 西红柿

- [Category:Tomatoes](https://commons.wikimedia.org/wiki/Category:Tomatoes)

### 大豆

- [Category:Soybeans](https://commons.wikimedia.org/wiki/Category:Soybeans)

### 玉米

- [Category:Maize](https://commons.wikimedia.org/wiki/Category:Maize)

### 猪肉

- [Category:Pork](https://commons.wikimedia.org/wiki/Category:Pork)

## 6. 图片存储方案

不建议前端直接依赖第三方图片外链。

正式方案：

- 将审核后的图片下载到本地仓库
- 前端统一从本地静态目录读取

建议目录：

```text
frontend/public/images/products/
├── garlic.jpg
├── napa-cabbage.jpg
├── egg.jpg
├── apple.jpg
├── tomato.jpg
├── soybean.jpg
├── maize.jpg
└── pork.jpg
```

## 7. 图片元数据方案

每张图片都必须维护元数据，建议使用单独的清单文件进行管理。

建议字段：

- `product_name`
- `file_name`
- `display_name`
- `source_page`
- `license`
- `author`
- `attribution_required`
- `alt`

后续建议新增文件：

- `frontend/src/data/product-image-manifest.js`

## 8. 前端展示方案

### 8.1 系统概览页

建议展示位置：

- 今日涨跌榜卡片左侧缩略图
- 重点监测品种趋势卡片头图

### 8.2 数据查询页

建议展示位置：

- 表格第一列显示“图片 + 品名”
- 点击行可显示侧边详情卡片

### 8.3 预测预警页

建议展示位置：

- 预测主品种标题区显示产品主图
- 预警列表项可显示小图

### 8.4 后续统计分析页

建议展示位置：

- 图表上方显示当前分析品种缩略图和简介

## 9. 图片开发顺序

### 第一阶段

- 确定重点 8 个品种
- 选定每个品种 1 张主图
- 下载到本地静态目录
- 建立图片元数据清单

### 第二阶段

- 改造前端组件支持图片展示
- 在系统概览页接入图片
- 在查询页接入图片
- 在预测预警页接入图片

### 第三阶段

- 增加缺省占位图
- 增加图片加载失败兜底
- 增加图片来源说明页

## 10. 图片授权执行规则

后续实际下载图片时必须遵守：

- 每张图逐张记录来源页
- 每张图逐张记录许可类型
- 每张图逐张记录作者
- 如果图片有署名要求，必须在系统页脚或说明页中展示

## 11. 当前结论

本项目已经确定：

- 价格数据继续使用官方源
- 图片资源单独维护
- 图片优先采用 Wikimedia Commons 或自有拍摄素材
- 图片最终本地化，供前端稳定展示

下一阶段可以直接开始：

- 建立产品图片目录
- 生成图片元数据清单
- 改造前端页面接入图片展示
