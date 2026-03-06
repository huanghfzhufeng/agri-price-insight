# PYBS 农产品价格分析可视化系统

这是一个适合毕业设计继续扩展的全栈项目骨架，目标是实现：

- 农产品价格数据采集与入库
- 多维度价格查询与统计分析
- 趋势预测与异常预警
- Web 可视化展示

当前版本已经包含：

- FastAPI 后端接口
- SQLite 演示数据库与自动灌入示例数据
- React + Vite + Tailwind 前端
- 与页面联动的仪表盘、查询、预警模块

## 项目结构

```text
PYBS/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── api/            # 路由层
│   │   ├── core/           # 配置
│   │   ├── db/             # 数据库连接
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 返回模型
│   │   └── services/       # 种子数据与分析逻辑
│   └── requirements.txt
├── frontend/               # React 前端
│   ├── src/
│   │   ├── api/            # 接口请求
│   │   ├── components/     # 复用组件
│   │   ├── utils/          # 图表与格式化工具
│   │   └── views/          # 页面视图
├── project_plan.md         # 毕业设计实施方案
└── README.md
```

## 后端启动

建议使用 Python 3.11 虚拟环境运行毕业设计项目。当前这台机器实际是 `Python 3.14.3`，能跑当前骨架，但如果你后面要接 `Prophet` 等时间序列库，通常更稳妥的做法是单独建一个 `Python 3.11` 环境。

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

启动后接口文档地址：

- [http://localhost:8000/docs](http://localhost:8000/docs)

后端首次启动会自动：

- 创建 `backend/pybs.db`
- 建表
- 灌入演示数据

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

默认访问地址：

- [http://localhost:5173](http://localhost:5173)

开发模式下 Vite 已经配置了 `/api` 代理到 `http://localhost:8000`。

## 当前已完成页面

- `系统概览`
- `数据查询`
- `预测预警`

## 后续建议优先扩展

1. 增加真实数据采集脚本
2. 将 SQLite 切换为 MySQL
3. 为“统计分析”接入 ECharts 图表
4. 为“系统管理”增加登录、数据源管理、任务调度和日志
5. 将预测基线模型替换为 Prophet / XGBoost 对比实验

## 你这个骨架的答辩价值

这个版本已经不是静态页面稿，而是：

- 有前后端分层
- 有数据库结构
- 有接口设计
- 有可运行演示
- 有后续扩展空间

它适合继续写成完整毕业设计《基于 Python 的农产品价格数据分析、预测与可视化系统的设计与实现》。
