# 部署文档

## 1. 本地演示部署

### 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## 2. SQLite 演示模式

默认模式使用 SQLite，数据库文件位于：

- `backend/pybs.db`

适合：

- 论文演示
- 本地答辩
- 单机开发

## 3. MySQL 部署模式

1. 新建数据库，例如 `agri_price_insight`
2. 修改 `backend/.env`

示例：

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/agri_price_insight
```

3. 运行 Alembic 迁移

```bash
cd backend
source .venv/bin/activate
alembic revision --autogenerate -m "init schema"
alembic upgrade head
```

4. 启动后端服务

## 4. 定时任务说明

系统支持 APScheduler 定时任务，默认关闭。

开启方式：

```env
SCHEDULER_ENABLED=true
DAILY_SYNC_HOUR=9
DAILY_SYNC_MINUTE=0
MONTHLY_SYNC_DAY=1
MONTHLY_SYNC_HOUR=10
MONTHLY_SYNC_MINUTE=0
```

## 5. 静态资源说明

- 前端图片目录：`frontend/public/images/products`
- 月报归档目录：`backend/data/monthly_reports`

## 6. 答辩前推荐操作

1. 执行一次日采集脚本
2. 执行一次月报同步脚本
3. 启动前后端并验证登录
4. 检查统计分析页、预警页和系统管理页
5. 导出一次 CSV 作为答辩演示材料
