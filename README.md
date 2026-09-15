# FeedbackOS

FeedbackOS 是面向 5～50 人 SaaS 与 AI 产品团队的反馈决策工作台。它希望持续回答两个问题：

1. 下周最应该解决哪三个用户问题，为什么？
2. 某次版本发布后，这些问题是否真的得到改善？

项目的核心不是生成一份看似合理的 AI 摘要，而是让每个主题、优先级和建议都能追溯到原始反馈证据。

## 当前状态

> Early development：项目尚未达到可用 MVP，请勿用于处理真实客户数据。

当前正在实施 OpenSpec 变更 `build-week-two-import-foundation`，已完成 7/35 个任务：

- 已核验并锁定基础依赖版本。
- 已初始化 Next.js、FastAPI 和共享契约工作区。
- 已配置 PostgreSQL 与 Garage 本地开发服务。
- 已建立分层配置、生产密钥校验、Alembic 骨架和统一命令。
- 已建立 Next.js 与 FastAPI 健康检查及 Web 同源 `/api` 代理。
- 已将权威设计 token 映射为项目内浅色/深色 Ant Design 主题和语义 CSS 变量。
- 已搭建认证页、工作空间/项目壳层和项目导入三步流的可访问路由骨架。
- 下一步是从 FastAPI OpenAPI 生成 TypeScript 类型与 API 客户端边界。

用户访谈、真实样本和付费意愿验证仍未完成。工程进度不代表产品需求已经得到验证。

## MVP 闭环

```text
上传反馈 → 清洗与脱敏 → 主题分析 → 原文证据 → Top 3 问题
         → 关联产品版本 → 发布前后对比 → 导出或创建任务
```

主要工程原则：

- AI 结论必须绑定原始反馈 ID，并允许下钻查看证据。
- 数量、比例和趋势由 SQL 或确定性程序计算，不交给大模型猜测。
- 原始文件在分析前完成敏感信息识别与脱敏。
- 工作空间之间执行严格的数据与权限隔离。
- 每次分析保存模型、Prompt、Embedding、规则和数据版本。

## 技术栈

- Web：Next.js、React、TypeScript、Ant Design。
- API：FastAPI、Pydantic、SQLAlchemy、Alembic。
- 数据库：PostgreSQL；后续使用 pgvector 保存语义向量。
- 对象存储：本地和 CI 使用 Garage，测试与生产计划接入阿里云 OSS。
- 数据处理：Polars、openpyxl、scikit-learn。
- 异步任务：后续使用 Redis 与 Celery Worker。
- 开发环境：Docker Compose、pnpm workspace、uv。

## 目录结构

```text
feedbackos/
├── apps/
│   ├── web/          # Next.js Web 应用
│   └── api/          # FastAPI API
├── packages/
│   └── contracts/    # 前后端共享契约
├── infra/            # 本地基础设施配置
├── docs/             # 架构与技术决策
├── openspec/         # 需求、设计与任务
├── compose.yaml
└── PROJECT_PLAN.md
```

## 本地开发

### 前置环境

- Node.js 24
- pnpm 11.19
- Python 3.13.12
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop 或兼容 Docker Compose 的运行环境

### 安装与启动

```bash
cp .env.example .env
pnpm install --frozen-lockfile
uv sync --project apps/api --frozen
pnpm dev
```

默认服务地址：

- Web：<http://localhost:3000>
- API 文档：<http://localhost:8000/docs>
- PostgreSQL：`127.0.0.1:5432`
- Garage S3 API：`127.0.0.1:3900`

`.env.example` 中仅包含本地公开测试值。不要把真实 OSS 凭据、会话密钥或客户数据提交到仓库。

### 常用命令

```bash
pnpm infra:up       # 启动 PostgreSQL 与 Garage 并等待健康检查
pnpm infra:status   # 查看基础设施状态
pnpm db:migrate     # 执行数据库迁移
pnpm lint           # API 与 Web Lint
pnpm typecheck      # Python 与 TypeScript 类型检查
pnpm test           # API 与 Web 测试
pnpm build:web      # Next.js 生产构建
pnpm infra:down     # 停止本地基础设施
```

## 开发与提交方式

- `main` 只保留已完成相应验证、可以继续集成的版本。
- 每个 OpenSpec 任务从 `main` 创建短期分支，例如 `codex/opsx-1.5-health-proxy`。
- 一个提交只表达一个清晰变更；实现、测试或迁移较大时可拆成多个原子提交。
- 合并前运行与改动相称的 Lint、类型检查、测试和构建。
- 暂不维护长期 `dev` 分支；出现共享测试环境或多人并行集成需求时再引入。

## 项目文档

- [项目计划](PROJECT_PLAN.md)
- [项目协作规范](AGENTS.md)
- [依赖版本决策](docs/decisions/0001-dependency-baseline.md)
- [第二周导入基础 OpenSpec](openspec/changes/build-week-two-import-foundation/)

## License

本项目使用 [MIT License](LICENSE)。
