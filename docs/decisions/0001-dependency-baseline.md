# 第二周依赖基线

状态：Accepted
核验日期：2026-09-10（Asia/Shanghai）

## 选择原则

- 只选择上游标记为稳定或 LTS 的版本，不使用 beta、RC 或 nightly。
- 应用直接依赖记录明确版本，完整传递依赖由锁文件固定。
- Node.js 使用 LTS 而不是 Current；Python 使用仍处于 bugfix 阶段且生态成熟的 3.13，而不抢先采用即将发布的 3.15。
- 本地/CI 对象存储使用 Garage，测试/生产首先使用阿里云 OSS；应用只调用两端共同支持的 S3 API。
- 此文档是 2026-09-10 的决策快照，不代表以后自动升级；升级必须重新运行测试和契约检查。

## 运行时与基础设施

| 依赖 | 固定版本 | 选择理由 | 官方来源 |
| --- | --- | --- | --- |
| Node.js | 24.21.0 | 当前 LTS；Next.js 生产应用不使用 Current 版本 | [Node.js releases](https://nodejs.org/en/about/previous-releases) |
| pnpm | 11.19.0 | 与当前工具链一致，并通过 `packageManager` 固定 | [pnpm package](https://www.npmjs.com/package/pnpm) |
| Python | 3.13.12 | 仍处于 bugfix 支持期；上游已发布 3.13.15，但当前 `uv` 托管运行时可重复安装的最新 3.13 版本是 3.13.12，因此暂时精确固定 | [Python downloads](https://www.python.org/downloads/) |
| PostgreSQL | 18.6 | 当前正式主版本的最新补丁；不采用 PostgreSQL 19 Beta | [PostgreSQL release notes](https://www.postgresql.org/docs/release/) |
| Garage | 2.4.1 | 官方 release build；用于本地和 CI 的 S3 兼容对象存储 | [Garage release builds](https://garagehq.deuxfleurs.fr/_releases.html) |
| 阿里云 OSS | 托管服务 | 用于测试和生产；发布前验证 S3 兼容差异 | [OSS S3 兼容性](https://help.aliyun.com/zh/oss/developer-reference/compatibility-with-amazon-s3) |

## Web 直接依赖

| 依赖 | 固定版本 | 选择理由 | 官方来源 |
| --- | --- | --- | --- |
| Next.js | 16.3.4 | 当前 npm stable，作为 Web 与同源 API 代理框架 | [next on npm](https://www.npmjs.com/package/next) |
| React / React DOM | 19.3.0 | 与当前 Next.js stable 的 peer 范围一致 | [react on npm](https://www.npmjs.com/package/react) |
| TypeScript | 6.0.3 | 已核验 TypeScript 7.0.2 为 npm stable，但 Next.js 16.3.4 携带的 `typescript-eslint` 8.70.0 明确不支持 TS 7；因此固定当前可完成类型检查、Lint 和生产构建的最新 TS 6 稳定版 | [typescript on npm](https://www.npmjs.com/package/typescript) |
| Ant Design | 6.6.3 | 当前 npm stable，统一通过 `ConfigProvider` 消费项目 token | [antd on npm](https://www.npmjs.com/package/antd) |
| openapi-typescript | 7.13.0 | 从 FastAPI 的 OpenAPI JSON 生成无运行时代码的 TypeScript 类型 | [openapi-typescript on npm](https://www.npmjs.com/package/openapi-typescript) |
| openapi-fetch | 0.17.0 | 以生成的 `paths` 类型约束同源 `/api` 请求，不再手写重复 DTO | [openapi-fetch on npm](https://www.npmjs.com/package/openapi-fetch) |

## API 与数据直接依赖

| 依赖 | 固定版本 | 选择理由 | 官方来源 |
| --- | --- | --- | --- |
| FastAPI | 0.141.1 | 当前 PyPI stable，提供 OpenAPI 与类型化请求边界 | [FastAPI on PyPI](https://pypi.org/project/fastapi/) |
| Pydantic | 2.13.5 | 当前 PyPI stable，用于输入、输出和环境配置校验 | [Pydantic on PyPI](https://pypi.org/project/pydantic/) |
| SQLAlchemy | 2.0.52 | 当前 PyPI stable，使用 2.x typed ORM API | [SQLAlchemy on PyPI](https://pypi.org/project/SQLAlchemy/) |
| Alembic | 1.19.2 | 当前 PyPI stable，与 SQLAlchemy 迁移链配套 | [Alembic on PyPI](https://pypi.org/project/alembic/) |
| Polars | 1.44.2 | 当前 PyPI stable，用于有界 CSV 解析和后续数据管道 | [Polars on PyPI](https://pypi.org/project/polars/) |
| openpyxl | 3.1.5 | 当前 PyPI stable，用只读模式预览 XLSX | [openpyxl on PyPI](https://pypi.org/project/openpyxl/) |

## 兼容边界

第二周只依赖 `PutObject`、`HeadObject`、`GetObject` 和 `DeleteObject` 及必要的对象元数据。Garage 本地测试使用 path-style Endpoint；OSS 使用 virtual-hosted-style Endpoint。不得根据 ETag 大小写或分片 ETag 算法推断文件内容哈希，内容幂等性统一使用应用在上传过程中计算的 SHA-256。

## 核验方式

- npm 包使用 `pnpm view <package>@<version> version` 确认可解析。
- Python 包使用隔离的 `uv run --with <package>==<version>` 完成解析和导入。
- Python 运行时使用 `uv python list 3.13 --only-downloads` 确认精确版本在新机器上可安装；待 `uv` 提供更新补丁版时单独升级。
- PostgreSQL 与 Garage 使用官方容器仓库的精确 tag；任务 1.3 启动后再固定镜像 digest。
