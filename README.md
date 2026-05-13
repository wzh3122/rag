# Mainland Legal Agent RAG

中国大陆法律多 Agent + 法规库 RAG 后端骨架。v1 目标是先搭稳可本地运行、可开源到 GitHub 的后端结构, 包括 FastAPI 接口、LangGraph 工作流、Provider 抽象、数据库层、RAG 空库降级、Review 与基础安全机制。

本项目仅用于学习、研究和一般法律信息参考, 不构成正式法律意见。使用者应自行配置模型、embedding、reranker 等服务的 API Key, 并承担相应调用费用。请勿将 `.env`、API Key、日志、数据库文件、用户聊天记录或付费数据提交到公开仓库。

## 功能范围

- `POST /legal-qa`: 非流式中国大陆法律问答。
- `POST /legal-qa/stream`: POST + NDJSON 阶段级流式响应。
- `/`: 内置对话式前端界面, 支持领域、地区、流式阶段展示和 sources 展示。
- 支持 `session_id` 多轮会话、事实累积、严重事实不足追问、明显事实冲突追问。
- 支持 DeepSeek / OpenAI-compatible LLM、Embedding、Reranker Provider 抽象。
- 预留 Qdrant 语义检索与 OpenSearch BM25 检索连接层。
- 默认 mock provider, 没有真实 API Key 也能跑单元测试。
- 当没有可靠 `sources` 时进入 `general_reference`, 不编造法条、案例、URL 或来源。

## 当前限制

v1 不做前端、登录、文件上传、OCR、法规爬虫、真实法规入库、批量 embedding、OpenSearch 真实索引构建、Qdrant 真实向量写入、Redis 限流和正式法律意见生成。

## 技术栈

Python, FastAPI, LangGraph, SQLAlchemy, SQLite/PostgreSQL, pydantic-settings, httpx, Qdrant, OpenSearch, OpenAI-compatible API, pytest。

## 安装

```bash
cd C:\Users\wzh\Desktop\rag
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

默认代码未附带任何作者 API Key。复制 `.env.example` 后, 请把 `.env` 中的 DeepSeek、embedding、reranker 等配置替换为你自己的服务配置。若只想本地 mock 运行, 可将 `.env` 中 `LLM_PROVIDER`、`EMBEDDING_PROVIDER`、`RERANKER_PROVIDER` 改为 `mock`。

## 启动

基础设施可选:

```bash
docker compose up -d
```

启动后端:

```bash
uvicorn app.main:app --reload
```

打开前端对话界面:

```text
http://127.0.0.1:8000/
```

健康检查:

```bash
curl http://127.0.0.1:8000/health
```

## API 示例

```bash
curl -X POST http://127.0.0.1:8000/legal-qa ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":null,\"message\":\"公司拖欠工资三个月, 我可以离职并要求补偿吗?\",\"legal_domain\":\"labor\",\"region\":\"广东\"}"
```

空法规库默认返回 `general_reference`, 只提供一般处理思路和证据清单。

流式接口:

```bash
curl -N -X POST http://127.0.0.1:8000/legal-qa/stream ^
  -H "Content-Type: application/json" ^
  -H "Accept: application/x-ndjson" ^
  -d "{\"message\":\"公司拖欠工资三个月, 我可以离职并要求补偿吗?\",\"legal_domain\":\"labor\"}"
```

多轮会话:

```json
{
  "session_id": "上一次响应里的 session_id",
  "message": "我还有工资流水和聊天记录",
  "legal_domain": "labor",
  "region": "广东"
}
```

## 配置说明

- `DATABASE_URL=sqlite:///./data/legal_agent_rag.db`: 默认 SQLite。
- PostgreSQL 示例: `postgresql+psycopg://legal_user:change_me@localhost:5432/legal_agent_rag`。
- `RAG_INDEX_READY=false`: 允许 Qdrant/OpenSearch 空库或未启动时优雅降级。
- 生产环境不要使用 `allow_origins=["*"]`; 请配置 `FRONTEND_CORS_ORIGINS` 白名单。
- 生产环境默认不保存聊天原文, 只保存必要状态和脱敏摘要。

## 测试

```bash
pytest
```

集成测试默认跳过。只有显式设置:

```bash
set RUN_INTEGRATION_TESTS=true
pytest tests/integration
```

才会尝试连接真实 LLM / Qdrant / OpenSearch。测试不会打印 API Key。

## 开源安全检查清单

- [ ] `.env` 没有被提交
- [ ] `.env.example` 只包含占位符
- [ ] 源码里没有真实 API Key
- [ ] README 没有暴露真实服务地址、密钥、账号
- [ ] `docker-compose.yml` 没有生产密码
- [ ] `data/` 目录没有被提交
- [ ] `logs/` 目录没有被提交
- [ ] SQLite / PostgreSQL dump 没有被提交
- [ ] Agent trace 没有被提交
- [ ] 用户聊天记录没有被提交
- [ ] 测试样例不包含真实个人信息
- [ ] 付费数据或付费接口返回内容没有被提交
- [ ] Git history 中没有误提交过密钥

检查命令:

```bash
git status
git log --all -- .env
```

如果误提交过密钥, 应立即轮换密钥。

## 后续路线

v2 接入法规采集、解析、入库、向量化与索引构建。v3 增加评估集、前端、用户系统、Redis/API Gateway 限流和生产部署方案。
