"""Chinese language pack. Keys must stay identical to locales/en.py."""

STRINGS = {
    # shell / navigation
    "app_title": "RAG 智能客服框架",
    "nav_chat": "智能客服对话",
    "nav_admin": "用量管理后台",
    "chat_title": "智能客服对话",
    "chat_subtitle": "仅基于知识库内容作答，回答下方展示引用来源。",
    "admin_title": "用量管理后台",
    "admin_subtitle": "按时间范围查看调用量、Token 消耗、耗时与拒答情况。",

    # sidebar / documents
    "sidebar_docs": "知识库文档",
    "upload_label": "上传文档（PDF / Word / Txt / Md）",
    "upload_hint": "仅支持文本型文件，扫描件 OCR 不在支持范围内。",
    "rebuild_index": "重建索引",
    "clear_chat": "清空对话",
    "docs_empty": "暂无文档，请先上传。",
    "doc_delete": "删除文档",
    "upload_success": "文档已保存，请点击“重建索引”使其生效。",
    "upload_failed": "上传失败：",
    "rebuild_success": "索引已重建，新文档立即可用。",
    "rebuild_empty": "知识库中没有可索引的文档。",

    # chat
    "chat_placeholder": "请输入您的问题…",
    "sources_title": "引用来源",
    "source_page": "第 {page} 页",
    "thinking": "正在检索并生成回答…",

    # agent
    "agent_name": "KnowledgeBaseSupportAgent",
    "agent_instructions": (
        "你是一名严格受控的知识库客服助手。必须遵守以下规则：\n"
        "1. 你只能依据 search_kb 工具返回的内容回答用户问题，禁止使用自己的先验知识或推测。\n"
        "2. 回答要简洁、准确；如果内容中包含来源信息，请在回答中说明依据的文件名与页码。\n"
        "3. 当 search_kb 返回标记 {marker}，或返回的内容不足以回答用户问题时，"
        "你必须原样输出下面这段固定文案，一个字都不能改，也不要添加任何解释或标点：\n"
        "{fallback}\n"
        "4. 严禁编造任何事实、数字、链接、订单号或来源。\n"
        "5. 始终使用中文回答。"
    ),
    "tool_search_kb": (
        "在知识库中检索与用户问题相关的原文片段，返回片段文本及其来源文件名和页码。"
        "当用户问题涉及产品资料、规格、使用方法或任何可能写在文档中的内容时必须调用此工具。"
        "如果知识库中没有相关内容，会返回专门的空结果标记。"
    ),
    "fallback_answer": "抱歉，知识库中暂无相关内容，我无法回答这个问题。",
    "no_relevant": "NO_RELEVANT_CONTENT",

    # admin
    "range_label": "统计范围",
    "range_7d": "近 7 天",
    "range_30d": "近 30 天",
    "metric_calls": "总调用次数",
    "metric_tokens": "总 Tokens",
    "metric_latency": "平均耗时 (ms)",
    "metric_unknown": "不知道占比 (%)",
    "chart_daily_calls": "每日调用次数",
    "chart_daily_tokens": "每日总 Tokens",
    "chart_token_split": "Prompt 与 Completion Tokens 对比",
    "chart_answer_ratio": "正常回答 vs 不知道占比",
    "chart_latency_trend": "每日平均耗时趋势",
    "axis_date": "日期",
    "axis_calls": "调用次数",
    "axis_tokens": "Tokens",
    "axis_ms": "耗时 (ms)",
    "axis_percent": "占比 (%)",
    "legend_normal": "正常回答",
    "legend_unknown": "不知道",
    "legend_prompt": "Prompt Tokens",
    "legend_completion": "Completion Tokens",
    "log_table_title": "日志明细",
    "search_placeholder": "按问题关键词搜索…",
    "col_time": "时间",
    "col_question": "问题",
    "col_called_kb": "检索知识库",
    "col_sources": "来源",
    "col_model": "模型",
    "col_prompt_tokens": "Prompt Tokens",
    "col_completion_tokens": "Completion Tokens",
    "col_total_tokens": "总 Tokens",
    "col_latency": "耗时 (ms)",
    "col_unknown": "不知道",
    "value_yes": "是",
    "value_no": "否",
    "no_data": "当前范围内暂无数据。",

    # errors
    "err_no_docs": "知识库中没有可索引的文档。",
    "err_no_llm_model": "请先在 .env 中配置 LLM_MODEL 和 LLM_API_KEY。",
    "err_no_embedding_model": "请先在 .env 中配置 EMBEDDING_MODEL。",
    "err_upload_type": "不支持的文件类型。",

    # evaluation
    "eval_header": "RAG 验收报告",
    "eval_ok": "通过",
    "eval_fail": "未通过",
    "eval_summary": "结果：{correct}/{total} 道通过（要求 ≥ 18/20）",
}
