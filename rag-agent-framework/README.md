# RAG Agent 接单框架（v1）

一个最小可用、可复用的 RAG 客服智能体框架。换文档、改提示词、加工具即可交付下一个项目。

## 快速开始

```bash
# 1. 复制环境变量模板并填写模型与密钥
cp .env.example .env

# 2. 安装依赖
python -m pip install -r requirements.txt

# 3. 启动演示与管理界面
streamlit run app.py
```

在侧边栏上传文本型 PDF / Word / Txt / Md，点击「重建索引」即可开始问答。

## 配置

所有密钥、模型与路径集中在 `.env` 与 `config.py`，代码中没有硬编码的模型名或厂商。

| 变量 | 说明 |
| --- | --- |
| `LLM_API_KEY` / `LLM_MODEL` | Agent 对话模型，必填 |
| `LLM_BASE_URL` | 可选；填写后自动切换为 Chat Completions 协议并关闭 tracing |
| `EMBEDDING_API_KEY` / `EMBEDDING_BASE_URL` | 留空则复用 LLM 配置 |
| `EMBEDDING_MODEL` | Embedding 模型，必填 |
| `DATABASE_URL` | 默认 `sqlite:///data/audit.db`；改成 PostgreSQL DSN 即可无缝迁移 |
| `SCORE_THRESHOLD` | 片段相关性阈值，默认 0.45 |

LLM 与 Embedding 配置相互独立，兼容「LLM 用 A 服务、Embedding 用 B 服务」以及任意 OpenAI 协议中转接口。

切块大小 512、重叠 50、检索 `top_k=5`、保留最近 6 轮对话，均在 `config.py` 中调整。

## 关键设计约束

- **零二次 LLM 调用**：`kb/` 中 `Settings.llm = None`，`search_kb()` 只调用 `index.as_retriever()`，返回原始节点文本与来源 metadata；绝不调用 `query_engine`。所有对话生成与 Token 消耗归口 OpenAI Agents SDK。
- **业务与展示解耦**：`kb/`、`agent/`、`audit/` 均不 `import streamlit`，可直接套 FastAPI。
- **来源可审计**：`called_kb` 与命中来源由 `RunContextWrapper` 在工具调用中写入，不解析模型回复文本。
- **真实用量**：Token 取自流式结束后的 `result.context_wrapper.usage`。
- **安全热重建**：通过 Chroma 的 `delete_collection` 清空旧索引，不用 `shutil.rmtree`；重建后清理 `@st.cache_resource`，无需重启。
- **精准拒答**：检索为空或未调用知识库时强制返回语言包中的固定文案，日志据此判定 `is_unknown`。

## 目录

```text
app.py / admin.py     Streamlit 单应用双页面
config.py / i18n.py   配置与语言包加载
locales/              zh.py / en.py，键名保持一致
kb/                   文档读取、切块向量化、检索
agent/                function_tool 与 Agent 服务
audit/                SQLAlchemy 2.0 日志与查询
eval.py               自动验收脚本
eval_samples/         示例手册 + 20 道测试题
```

## 接单二开

1. **换知识库**：把文档放入 `data/docs/`，在页面点击「重建索引」。
2. **改话术/拒答**：编辑 `locales/zh.py` 与 `locales/en.py` 中的 `agent_instructions`、`fallback_answer`、`tool_search_kb`。
3. **加业务工具**：只在 `agent/tools.py` 中新增 `@function_tool`，并在 `agent/service_agent.py` 的 `tools=[...]` 注册。
4. **换语言**：把 `config.py` 的 `LANGUAGE` 改为 `"en"` 后重启，界面、提示词、工具描述、拒答文案与图表标题全部切换。

## 验收

```bash
python eval.py
```

脚本会用 `eval_samples/product_manual.md` 建独立索引，跑 12 道可答题 + 8 道不可答题，输出逐题结果与 `data/eval_report.json`；≥ 18/20 返回退出码 0。

手动验收：完成 10 次问答后进入「用量管理后台」，应看到 10 条日志、真实 Token 统计和 5 张 Plotly 图表；上传新 PDF 并重建索引后无需重启即可基于新文档作答。
