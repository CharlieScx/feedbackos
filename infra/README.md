# Infrastructure

FeedbackOS 的本地基础设施配置放在此目录。根目录的 `compose.yaml` 启动：

- PostgreSQL 18.6，数据保存在命名卷 `feedbackos_postgres_data`。
- Garage 2.4.1，元数据和对象分别保存在命名卷中。
- Garage 首次启动自动创建私有 bucket `feedbackos-dev-private` 和本地专用访问密钥。

启动并等待健康检查：

```bash
docker compose up -d --wait
```

检查服务、集群和 bucket：

```bash
docker compose ps
docker compose exec garage /garage json-api GetClusterHealth
docker compose exec garage /garage bucket info feedbackos-dev-private
```

本地应用的 S3 Endpoint 是 `http://127.0.0.1:3900`，Region 是 `garage`，并应使用 path-style 寻址。这些固定密钥仅用于本机开发，不得复用到测试或生产。
