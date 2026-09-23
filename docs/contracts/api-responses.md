# API 响应契约

FastAPI 是响应结构与错误码的唯一来源，TypeScript 类型由 OpenAPI 生成。业务接口不得自行定义另一套成功或错误外壳。

## 成功响应

单个资源使用 `data`：

```json
{
  "data": {
    "id": "resource-id"
  }
}
```

列表使用 `data` 与 `pagination`：

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 0,
    "total_pages": 0
  }
}
```

## 错误响应

```json
{
  "error": {
    "code": "file_invalid",
    "message": "文件无效，请检查类型、大小或内容",
    "retryable": false,
    "field_errors": []
  }
}
```

前端 MUST 按 `code` 决定流程，`message` 只用于安全展示，不得把中文文案当作程序判断条件。

| 错误码 | HTTP | Web 动作 |
| --- | ---: | --- |
| `authentication_failed` | 401 | 进入认证流程 |
| `resource_not_found` | 404 | 展示不存在；跨租户资源也使用此码 |
| `file_invalid` | 422 | 返回文件选择或修正流程 |
| `idempotency_conflict` | 409 | 更换幂等键后重新发起 |
| `retryable_failure` | 503 | 保留上下文并允许重试 |

`access_denied`、`request_invalid`、`conflict` 与 `internal_error` 用于不属于上述五条业务分支的通用失败。

## 安全规则

- 错误响应和字段错误 MUST NOT 回显密码、Cookie、会话密钥、存储凭据、反馈原文、单元格值或内部异常文本。
- `field_errors` 只包含字段路径和稳定校验代码，不包含被拒绝的输入值。
- 无权访问另一个工作空间的资源时，使用 `resource_not_found`，不泄露资源是否存在。
- 只有明确标为 `retryable: true` 的失败，Web 才应提供原操作重试。
