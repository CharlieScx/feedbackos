# 数据库模型与事务边界

`apps/api/src/feedbackos_api/models.py` 定义第二周的九张表；生产建表由后续 3.2 的 Alembic 迁移负责，应用启动不会调用 `create_all()`。

## 归属与约束

- `User` 保存规范化邮箱和密码哈希，`Session` 只保存会话 token 哈希、过期和撤销时间。
- `Member` 以 `(workspace_id, user_id)` 唯一，角色限定为 `owner`、`member`。
- `Project` 必须属于一个已存在的工作空间。
- `DataSource`、`StoredFile`、`ImportBatch`、`FeedbackItem` 使用 `(workspace_id, project_id)` 复合外键关联项目。
- 批次通过三列复合外键引用同项目的数据源和文件；反馈通过同样方式引用所属批次，防止只传对 ID 却拼错租户或项目。
- `(created_by_id, project_id, idempotency_key)` 唯一；内容哈希不唯一，允许独立上传尝试，后续质量管道再处理重复反馈。
- 状态仅允许 `uploaded`、`preview_ready`、`mapping_confirmed`、`failed`。失败必须带安全错误码和可重试标记；状态转换与映射校验由后续服务负责。
- 标识符使用随机 UUID，时间使用带时区的数据库时间，枚举值以小写字符串落库并有 CHECK 约束。

数据库外键负责验证归属一致性，成员权限仍需由后续 API 从当前用户成员关系限定查询。外键不代替授权。

## 事务用法

```python
with get_database().transaction() as session:
    session.add(workspace)
    session.flush()
    session.add(owner_member)
```

退出上下文时提交；写入、flush 或 commit 失败时回滚并关闭会话。业务服务在返回成功响应前退出该边界，内部辅助函数可以 flush，但不单独 commit。同一事务内的多步写入全部成功才生效。

数据库连接使用现有 `FEEDBACKOS_DATABASE_URL`，连接池使用前置健康检查。SQL 参数被隐藏，避免异常日志带出凭据或反馈内容；仍不得自行记录原始 SQL 参数或拼接用户输入到 SQL。

删除外键默认阻止删除仍被引用的资源。后续删除服务需先完成对象存储清理与关联数据处理，不能仅依靠数据库级联删除对象元数据。

本地模型测试位于不提交的 `tests/api/test_models.py`：在开发 PostgreSQL 中创建随机 `test_models_*` schema，验证后只清理本次 schema。不要在生产库运行本地测试。数据库服务需要先通过 `docker compose up -d --wait postgres` 启动。
