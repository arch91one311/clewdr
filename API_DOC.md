# ClewdR API 接口文档 (v0.12.23)

## 基础信息

| 项 | 值 |
|---|---|
| Base URL | `http://127.0.0.1:8484` |
| 默认端口 | 8484 |
| 请求体大小限制 | 32 MB |
| 默认 max_tokens | 8192 |

## 认证方式

| 类型 | 方式 | 适用端点 |
|------|------|----------|
| Bearer Token | `Authorization: Bearer <API Password>` | 所有 API 端点 |
| X-API-Key | `X-API-Key: <API Password>` | `/v1/messages`、`/code/v1/messages` |
| Admin Token | `Authorization: Bearer <Admin Password>` | `/api/*` 管理端点 |

---

## 一、Claude Web 端点

### 1. POST `/v1/messages`

Claude 原生格式，支持流式。

**请求体：**

```json
{
  "model": "claude-sonnet-4-20250514",
  "messages": [
    {
      "role": "user",
      "content": "你好"
    }
  ],
  "max_tokens": 4096,
  "stream": false,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "stop_sequences": ["END"],
  "system": "你是一个助手",
  "thinking": {
    "type": "enabled",
    "budget_tokens": 10000
  },
  "tools": [],
  "tool_choice": "auto",
  "metadata": {}
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型标识符 |
| messages | array | 是 | 消息列表 |
| messages[].role | string | 是 | `"user"` / `"assistant"` / `"system"` |
| messages[].content | string / array | 是 | 文本或 ContentBlock 数组 |
| max_tokens | u32 | 是 | 最大输出 token 数 |
| stream | boolean | 否 | 是否流式返回，默认 false |
| temperature | f32 | 否 | 采样温度，0-1 |
| top_p | f32 | 否 | Nucleus 采样参数 |
| top_k | u32 | 否 | Top-K 采样参数 |
| stop_sequences | string[] | 否 | 自定义停止序列 |
| system | string / array | 否 | 系统提示 |
| thinking | object | 否 | 思维链配置 |
| thinking.type | string | 否 | `"enabled"` / `"disabled"` / `"adaptive"` |
| thinking.budget_tokens | u64 | 条件 | type 为 `"enabled"` 时必填 |
| tools | array | 否 | 工具列表 |
| tool_choice | string / object | 否 | `"auto"` / `"any"` / `"none"` 或指定工具 |
| metadata | object | 否 | 自定义元数据 |
| output_config | object | 否 | 输出能力配置 |
| output_format | object | 否 | JSON Schema 输出格式 |
| service_tier | string | 否 | `"auto"` / `"standard_only"` |
| n | u32 | 否 | 生成数量 |

**ContentBlock 类型：**

| 类型 | 说明 |
|------|------|
| text | 文本内容 |
| image | 图片（base64） |
| document | 文档 |
| search_result | 搜索结果 |
| thinking | 思维链内容 |
| tool_use | 工具调用 |
| tool_result | 工具返回结果 |
| image_url | 图片 URL |

**响应体（非流式）：**

```json
{
  "id": "msg_xxx",
  "type": "message",
  "role": "assistant",
  "model": "claude-sonnet-4-20250514",
  "content": [
    {
      "type": "text",
      "text": "你好！"
    }
  ],
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20
  }
}
```

**stop_reason 取值：**

| 值 | 说明 |
|---|---|
| end_turn | 正常结束 |
| max_tokens | 达到最大 token 数 |
| stop_sequence | 匹配到停止序列 |
| tool_use | 调用工具 |
| pause_turn | 暂停 |
| refusal | 拒绝回复 |
| model_context_window_exceeded | 超出上下文窗口 |

**流式响应（`stream: true`）：**

返回 Server-Sent Events (SSE) 事件流：

```
event: message_start
data: {"type":"message_start","message":{...}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"你好"}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":20}}

event: message_stop
data: {"type":"message_stop"}
```

---

### 2. POST `/v1/chat/completions`

OpenAI 兼容格式，支持流式。

**请求体：**

```json
{
  "model": "claude-sonnet-4-20250514",
  "messages": [
    { "role": "system", "content": "你是一个助手" },
    { "role": "user", "content": "你好" }
  ],
  "max_tokens": 4096,
  "max_completion_tokens": 4096,
  "stream": false,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "stop": ["END"],
  "thinking": {
    "type": "enabled",
    "budget_tokens": 10000
  },
  "reasoning_effort": "high",
  "tools": [],
  "tool_choice": "auto",
  "frequency_penalty": 0.0,
  "n": 1
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型标识符 |
| messages | array | 是 | 消息列表 |
| max_tokens | u32 | 否 | 最大输出 token 数 |
| max_completion_tokens | u32 | 否 | 同 max_tokens，二选一 |
| stream | boolean | 否 | 是否流式返回 |
| temperature | f32 | 否 | 采样温度 |
| top_p | f32 | 否 | Nucleus 采样 |
| top_k | u32 | 否 | Top-K 采样 |
| stop | string[] | 否 | 停止序列 |
| thinking | object | 否 | 思维链配置 |
| reasoning_effort | string | 否 | `"low"` / `"medium"` / `"high"` |
| tools | array | 否 | 工具列表 |
| tool_choice | string / object | 否 | 工具选择策略 |
| frequency_penalty | f32 | 否 | 频率惩罚 |
| logit_bias | object | 否 | Logit 偏置 |
| n | u32 | 否 | 生成数量 |
| metadata | object | 否 | 自定义元数据 |

**响应体（非流式）：**

```json
{
  "id": "xxx",
  "object": "chat.completion",
  "created": 1773815731,
  "model": "claude-sonnet-4-20250514",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

**finish_reason 取值：**

| 值 | 说明 |
|---|---|
| stop | 正常结束 |
| length | 达到最大长度 |
| tool_calls | 工具调用 |
| content_filter | 内容过滤 |

**流式响应（`stream: true`）：**

返回 OpenAI 格式的 SSE 事件流：

```
data: {"id":"xxx","object":"chat.completion.chunk","created":1773815731,"model":"claude-sonnet-4-20250514","choices":[{"index":0,"delta":{"role":"assistant","content":"你"},"finish_reason":null}]}

data: {"id":"xxx","object":"chat.completion.chunk","created":1773815731,"model":"claude-sonnet-4-20250514","choices":[{"index":0,"delta":{"content":"好"},"finish_reason":null}]}

data: {"id":"xxx","object":"chat.completion.chunk","created":1773815731,"model":"claude-sonnet-4-20250514","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

---

### 3. GET `/v1/models`

获取可用模型列表。

**响应体：**

```json
{
  "object": "list",
  "data": [
    { "id": "claude-3-7-sonnet-20250219", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-3-7-sonnet-20250219-thinking", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-sonnet-4-20250514", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-sonnet-4-20250514-thinking", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-sonnet-4-20250514-1M", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-sonnet-4-5-20250929", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-sonnet-4-5-20250929-thinking", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-sonnet-4-5-20250929-1M", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-sonnet-4-6", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-sonnet-4-6-thinking", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-sonnet-4-6-1M", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-20250514", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-20250514-thinking", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-1-20250805", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-1-20250805-thinking", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-5-20251101", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-5-20251101-thinking", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-5", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-5-thinking", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-6", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-6-thinking", "object": "model", "created": 0, "owned_by": "clewdr" },
    { "id": "claude-opus-4-6-1M", "object": "model", "created": 0, "owned_by": "clewdr" }
  ]
}
```

**模型后缀说明：**

| 后缀 | 说明 |
|------|------|
| (无) | 标准模式 |
| -thinking | 启用思维链（Extended Thinking） |
| -1M | 1M 上下文窗口 |

---

## 二、Claude Code 端点

### 4. POST `/code/v1/messages`

Claude Code 原生格式。请求/响应格式同 `/v1/messages`。

额外处理：
- 自动注入 billing header
- 支持自定义系统提示（通过配置 `custom_system`）
- 支持 `anthropic-beta` 请求头透传
- 系统提示哈希缓存

---

### 5. POST `/code/v1/chat/completions`

Claude Code OpenAI 兼容格式。请求/响应格式同 `/v1/chat/completions`。

---

### 6. POST `/code/v1/messages/count_tokens`

Token 计数接口，不执行实际 API 调用。

**请求体：** 同 `/v1/messages`

**响应体：**

```json
{
  "input_tokens": 1234
}
```

---

### 7. GET `/code/v1/models`

获取可用模型列表。响应格式同 `/v1/models`。

---

## 三、管理端点

> 以下端点需要使用 Admin Password 认证。

### 8. GET `/api/auth`

验证管理员身份。

| 状态码 | 说明 |
|--------|------|
| 200 | 已认证 |
| 401 | 未认证 |

---

### 9. GET `/api/config`

获取当前配置。敏感字段（`cookie_array`、`wasted_cookie`）已自动移除。

**响应体示例：**

```json
{
  "ip": "127.0.0.1",
  "port": 8484,
  "max_retries": 5,
  "preserve_chats": false,
  "web_search": false,
  "sanitize_messages": true,
  "use_real_roles": false,
  "skip_first_warning": false,
  "skip_second_warning": false,
  "skip_restricted": false,
  "skip_non_pro": false,
  "skip_rate_limit": true,
  "skip_normal_pro": false,
  "proxy": null,
  "rproxy": null
}
```

---

### 10. POST `/api/config`

更新配置，支持热加载（ip 和 port 除外）。

**请求体：** 完整或部分配置对象

**响应体：**

```json
{
  "message": "Config updated successfully",
  "config": { "...更新后的配置..." }
}
```

---

### 11. POST `/api/cookie`

添加新 Cookie。

**请求体：**

```json
{
  "cookie": "sk-ant-sid02-xxxxx...",
  "supports_claude_1m_sonnet": true,
  "supports_claude_1m_opus": true
}
```

**响应：** 200 OK

---

### 12. PUT `/api/cookie`

更新 Cookie 的 1M 上下文支持设置。

**请求体：**

```json
{
  "cookie": "sk-ant-sid02-xxxxx...",
  "supports_claude_1m_sonnet": true,
  "supports_claude_1m_opus": false
}
```

**响应：** 200 OK

---

### 13. DELETE `/api/cookie`

删除 Cookie。

**请求体：**

```json
{
  "cookie": "sk-ant-sid02-xxxxx..."
}
```

**响应：** 204 No Content

---

### 14. GET `/api/cookies`

获取所有 Cookie 及其状态。

**查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| refresh | boolean | `true` 强制刷新，默认 false（5 分钟缓存） |

**响应头：**

| 头 | 说明 |
|---|---|
| X-Cache-Status | `HIT` 或 `MISS` |
| X-Cache-Timestamp | 响应时间戳 |

**响应体：**

```json
{
  "valid": [
    {
      "cookie": "sk-ant-sid02-xxx...",
      "reset_time": null,
      "supports_claude_1m_sonnet": true,
      "supports_claude_1m_opus": true,
      "session_utilization": 0.15,
      "session_resets_at": 1773830000,
      "seven_day_utilization": 0.05,
      "seven_day_resets_at": 1774300000,
      "seven_day_opus_utilization": 0.02,
      "seven_day_opus_resets_at": 1774300000,
      "seven_day_sonnet_utilization": 0.03,
      "seven_day_sonnet_resets_at": 1774300000
    }
  ],
  "exhausted": [],
  "invalid": []
}
```

---

### 15. GET `/api/version`

获取版本号，无需认证。

**响应：** 纯文本 `0.12.23`

---

## 四、快速测试

### 非流式请求

```bash
curl http://127.0.0.1:8484/v1/chat/completions \
  -H "Authorization: Bearer <API_PASSWORD>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

### 流式请求

```bash
curl http://127.0.0.1:8484/v1/chat/completions \
  -H "Authorization: Bearer <API_PASSWORD>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100,
    "stream": true
  }'
```

### 获取模型列表

```bash
curl http://127.0.0.1:8484/v1/models \
  -H "Authorization: Bearer <API_PASSWORD>"
```

### Token 计数

```bash
curl http://127.0.0.1:8484/code/v1/messages/count_tokens \
  -H "Authorization: Bearer <API_PASSWORD>" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "messages": [{"role": "user", "content": "Hello world"}],
    "max_tokens": 100
  }'
```

### 管理 Cookie

```bash
# 添加 Cookie
curl -X POST http://127.0.0.1:8484/api/cookie \
  -H "Authorization: Bearer <ADMIN_PASSWORD>" \
  -H "Content-Type: application/json" \
  -d '{"cookie": "sk-ant-sid02-xxxxx..."}'

# 查看 Cookie 状态
curl http://127.0.0.1:8484/api/cookies \
  -H "Authorization: Bearer <ADMIN_PASSWORD>"

# 删除 Cookie
curl -X DELETE http://127.0.0.1:8484/api/cookie \
  -H "Authorization: Bearer <ADMIN_PASSWORD>" \
  -H "Content-Type: application/json" \
  -d '{"cookie": "sk-ant-sid02-xxxxx..."}'
```
