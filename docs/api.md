# API

## POST /legal-qa

请求:

```json
{
  "session_id": null,
  "message": "公司拖欠工资三个月, 我可以离职并要求补偿吗?",
  "legal_domain": "labor",
  "region": "广东"
}
```

成功响应字段:

- `session_id`: 会话 ID。为空时自动创建。
- `status`: `completed`, `general_reference`, `clarification_needed`, `fact_conflict`, `insufficient_basis`, `out_of_scope`, `rate_limited`, `error`。
- `extracted_facts`: 规则抽取并累积的事实摘要。
- `sources`: 检索到并通过过滤的来源。空来源时不得编造法条。
- `final_answer`: 最终回答。
- `review`: Review Agent 检查结果。

## POST /legal-qa/stream

使用 POST + NDJSON:

```http
POST /legal-qa/stream
Content-Type: application/json
Accept: application/x-ndjson
```

事件类型:

- `session`
- `stage`
- `sources`
- `retry`
- `clarification_needed`
- `fact_conflict`
- `general_reference`
- `insufficient_basis`
- `final`
- `error`

示例:

```jsonl
{"type":"session","session_id":"abc123"}
{"type":"stage","agent":"fact_extractor","message":"正在提取关键事实"}
{"type":"final","data":{}}
```

## 状态语义

- `completed`: 有可靠 sources, 并通过 Review, 输出十段式回答。
- `general_reference`: 没有可靠 sources, 只输出一般参考。
- `clarification_needed`: 严重事实不足, 需要先追问。
- `fact_conflict`: 多轮事实冲突, 需要用户确认。
- `out_of_scope`: 超出中国大陆法律或 v1 支持范围。
- `rate_limited`: 同一 IP 对同一路径请求过于频繁。

