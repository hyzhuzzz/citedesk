"""Usage dashboard page.

Registered by ``app.py`` through ``st.navigation``.  Aggregation happens in
Pandas, never with SQLite-specific date functions, so PostgreSQL works too.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import i18n
from audit.logger import query_logs, to_dict

_COLUMNS = [
    "created_at",
    "question",
    "called_kb",
    "sources",
    "model",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "latency_ms",
    "is_unknown",
]


def _load_frame(days: int):
    start = datetime.now() - timedelta(days=days)
    logs = query_logs(start=start)
    frame = pd.DataFrame([to_dict(row) for row in logs], columns=_COLUMNS)
    if not frame.empty:
        frame["called_kb"] = frame["called_kb"].astype(bool)
        frame["is_unknown"] = frame["is_unknown"].astype(bool)
        frame["day"] = pd.to_datetime(frame["created_at"]).dt.date
    return start, logs, frame


def _daily(frame: pd.DataFrame, start: datetime, column: str, how: str = "sum"):
    days = pd.date_range(start=start.date(), end=datetime.now().date(), freq="D").date
    if frame.empty:
        return days, [0] * len(days)
    grouped = frame.groupby("day")[column]
    values = grouped.sum() if how == "sum" else grouped.mean()
    values = values.reindex(days, fill_value=0)
    return days, values.tolist()


def _layout(fig: go.Figure, title: str, y_title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        xaxis_title=i18n.t("axis_date"),
        yaxis_title=y_title,
        template="plotly_white",
        height=330,
        margin=dict(l=55, r=20, t=55, b=45),
        hovermode="x unified",
    )
    return fig


def _line(days, values, title: str, y_title: str) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=list(days),
            y=values,
            mode="lines+markers",
            line=dict(width=2, color="#2563EB"),
            marker=dict(size=6),
        )
    )
    return _layout(fig, title, y_title)


def render_admin_page() -> None:
    st.title(i18n.t("admin_title"))
    st.caption(i18n.t("admin_subtitle"))

    options = [7, 30]
    days = st.selectbox(
        i18n.t("range_label"),
        options=options,
        format_func=lambda value: i18n.t("range_7d") if value == 7 else i18n.t("range_30d"),
    )
    start, logs, frame = _load_frame(days)

    total_calls = len(frame)
    total_tokens = int(frame["total_tokens"].sum()) if not frame.empty else 0
    avg_latency = int(frame["latency_ms"].mean()) if not frame.empty else 0
    unknown_rate = round(float(frame["is_unknown"].mean()) * 100, 1) if not frame.empty else 0.0

    metric_columns = st.columns(4)
    metric_columns[0].metric(i18n.t("metric_calls"), total_calls)
    metric_columns[1].metric(i18n.t("metric_tokens"), total_tokens)
    metric_columns[2].metric(i18n.t("metric_latency"), avg_latency)
    metric_columns[3].metric(i18n.t("metric_unknown"), unknown_rate)

    st.divider()

    # Daily call counts are row counts, not a column sum.
    days_axis = pd.date_range(start=start.date(), end=datetime.now().date(), freq="D").date
    if frame.empty:
        calls = [0] * len(days_axis)
    else:
        calls = frame.groupby("day").size().reindex(days_axis, fill_value=0).tolist()

    _, daily_tokens = _daily(frame, start, "total_tokens")
    st.plotly_chart(
        _line(days_axis, calls, i18n.t("chart_daily_calls"), i18n.t("axis_calls")),
        use_container_width=True,
    )

    bar_tokens = go.Figure(
        go.Bar(x=list(days_axis), y=daily_tokens, marker_color="#7C3AED")
    )
    st.plotly_chart(
        _layout(bar_tokens, i18n.t("chart_daily_tokens"), i18n.t("axis_tokens")),
        use_container_width=True,
    )

    _, prompt_tokens = _daily(frame, start, "prompt_tokens")
    _, completion_tokens = _daily(frame, start, "completion_tokens")
    split = go.Figure()
    split.add_trace(
        go.Bar(x=list(days_axis), y=prompt_tokens, name=i18n.t("legend_prompt"), marker_color="#0EA5E9")
    )
    split.add_trace(
        go.Bar(x=list(days_axis), y=completion_tokens, name=i18n.t("legend_completion"), marker_color="#F59E0B")
    )
    split.update_layout(barmode="stack")
    st.plotly_chart(
        _layout(split, i18n.t("chart_token_split"), i18n.t("axis_tokens")),
        use_container_width=True,
    )

    answered = int((~frame["is_unknown"]).sum()) if not frame.empty else 0
    fallback = int(frame["is_unknown"].sum()) if not frame.empty else 0
    ratio = go.Figure(
        go.Pie(
            labels=[i18n.t("legend_normal"), i18n.t("legend_unknown")],
            values=[answered, fallback],
            hole=0.55,
        )
    )
    ratio.update_layout(title=i18n.t("chart_answer_ratio"), height=330, template="plotly_white")
    st.plotly_chart(ratio, use_container_width=True)

    _, latency = _daily(frame, start, "latency_ms", "mean")
    st.plotly_chart(
        _line(days_axis, latency, i18n.t("chart_latency_trend"), i18n.t("axis_ms")),
        use_container_width=True,
    )

    st.divider()
    st.subheader(i18n.t("log_table_title"))
    keyword = st.text_input(i18n.t("search_placeholder"))
    visible_logs = query_logs(start=start, keyword=keyword) if keyword else logs
    table = pd.DataFrame([to_dict(row) for row in visible_logs], columns=_COLUMNS)
    if not table.empty:
        table["called_kb"] = table["called_kb"].map(
            {True: i18n.t("value_yes"), False: i18n.t("value_no")}
        )
        table["is_unknown"] = table["is_unknown"].map(
            {True: i18n.t("value_yes"), False: i18n.t("value_no")}
        )
        table = table.rename(
            columns={
                "created_at": i18n.t("col_time"),
                "question": i18n.t("col_question"),
                "called_kb": i18n.t("col_called_kb"),
                "sources": i18n.t("col_sources"),
                "model": i18n.t("col_model"),
                "prompt_tokens": i18n.t("col_prompt_tokens"),
                "completion_tokens": i18n.t("col_completion_tokens"),
                "total_tokens": i18n.t("col_total_tokens"),
                "latency_ms": i18n.t("col_latency"),
                "is_unknown": i18n.t("col_unknown"),
            }
        )
    st.dataframe(table, use_container_width=True, hide_index=True)
