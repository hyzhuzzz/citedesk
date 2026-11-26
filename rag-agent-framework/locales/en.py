"""English language pack. Keys must stay identical to locales/zh.py."""

STRINGS = {
    # shell / navigation
    "app_title": "RAG Support Agent Framework",
    "nav_chat": "Support Chat",
    "nav_admin": "Usage Dashboard",
    "chat_title": "Support Chat",
    "chat_subtitle": "Answers are grounded in the knowledge base; citations are shown below each reply.",
    "admin_title": "Usage Dashboard",
    "admin_subtitle": "Calls, token usage, latency and fallback rate over the selected period.",

    # sidebar / documents
    "sidebar_docs": "Knowledge Base Documents",
    "upload_label": "Upload documents (PDF / Word / Txt / Md)",
    "upload_hint": "Text-based files only; scanned-document OCR is not supported.",
    "rebuild_index": "Rebuild Index",
    "clear_chat": "Clear Chat",
    "docs_empty": "No documents yet. Please upload some first.",
    "doc_delete": "Delete document",
    "upload_success": "Documents saved. Click 'Rebuild Index' to activate them.",
    "upload_failed": "Upload failed: ",
    "rebuild_success": "Index rebuilt. New documents are available immediately.",
    "rebuild_empty": "There are no documents to index.",

    # chat
    "chat_placeholder": "Type your question here...",
    "sources_title": "Sources",
    "source_page": "Page {page}",
    "thinking": "Retrieving and generating an answer...",

    # agent
    "agent_name": "KnowledgeBaseSupportAgent",
    "agent_instructions": (
        "You are a strictly grounded knowledge-base support assistant. Obey these rules:\n"
        "1. Answer only from the content returned by the search_kb tool. Never use prior "
        "knowledge, assumptions or guesses.\n"
        "2. Be concise and accurate. When source information is present, mention the file "
        "name and page number in your answer.\n"
        "3. When search_kb returns the marker {marker}, or when the returned content is "
        "insufficient to answer, you MUST output the exact fixed text below verbatim, "
        "without changing a single character and without adding any explanation or punctuation:\n"
        "{fallback}\n"
        "4. Never invent facts, figures, links, order numbers or sources.\n"
        "5. Always answer in English."
    ),
    "tool_search_kb": (
        "Retrieve original text snippets relevant to the user's question from the knowledge "
        "base, including each snippet's source file name and page number. Call this tool "
        "whenever the question could be answered by product documentation, specifications "
        "or usage guides. Returns a dedicated empty-result marker when nothing relevant exists."
    ),
    "fallback_answer": "Sorry, the knowledge base has no relevant content, so I cannot answer this question.",
    "no_relevant": "NO_RELEVANT_CONTENT",

    # admin
    "range_label": "Time range",
    "range_7d": "Last 7 days",
    "range_30d": "Last 30 days",
    "metric_calls": "Total Calls",
    "metric_tokens": "Total Tokens",
    "metric_latency": "Avg Latency (ms)",
    "metric_unknown": "Fallback Rate (%)",
    "chart_daily_calls": "Daily Calls",
    "chart_daily_tokens": "Daily Total Tokens",
    "chart_token_split": "Prompt vs Completion Tokens",
    "chart_answer_ratio": "Answered vs Fallback Ratio",
    "chart_latency_trend": "Daily Average Latency",
    "axis_date": "Date",
    "axis_calls": "Calls",
    "axis_tokens": "Tokens",
    "axis_ms": "Latency (ms)",
    "axis_percent": "Share (%)",
    "legend_normal": "Answered",
    "legend_unknown": "Fallback",
    "legend_prompt": "Prompt Tokens",
    "legend_completion": "Completion Tokens",
    "log_table_title": "Log Details",
    "search_placeholder": "Search questions by keyword...",
    "col_time": "Time",
    "col_question": "Question",
    "col_called_kb": "KB Called",
    "col_sources": "Sources",
    "col_model": "Model",
    "col_prompt_tokens": "Prompt Tokens",
    "col_completion_tokens": "Completion Tokens",
    "col_total_tokens": "Total Tokens",
    "col_latency": "Latency (ms)",
    "col_unknown": "Fallback",
    "value_yes": "Yes",
    "value_no": "No",
    "no_data": "No data in the selected range.",

    # errors
    "err_no_docs": "There are no documents to index.",
    "err_no_llm_model": "Please set LLM_MODEL and LLM_API_KEY in .env first.",
    "err_no_embedding_model": "Please set EMBEDDING_MODEL in .env first.",
    "err_upload_type": "Unsupported file type.",

    # evaluation
    "eval_header": "RAG Evaluation Report",
    "eval_ok": "PASS",
    "eval_fail": "FAIL",
    "eval_summary": "Result: {correct}/{total} passed (requirement: >= 18/20)",
}
