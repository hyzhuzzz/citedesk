"""Single Streamlit entry point: ``streamlit run app.py``.

``app.py`` owns the navigation shell and the chat page; ``admin.py`` supplies
the other page.  Core packages (kb/, agent/, audit/) never import Streamlit.
"""

from __future__ import annotations

import streamlit as st

import config
import i18n
from admin import render_admin_page
from agent.service_agent import run_chat_stream
from audit.logger import write_log
from kb.indexer import build_index
from kb.loader import delete_document, list_documents, save_uploaded_file
from kb.retriever import get_retriever

st.set_page_config(page_title=i18n.t("app_title"), layout="wide")


@st.cache_resource(show_spinner=False)
def cached_retriever():
    """Rebuilt from scratch after an index rebuild via ``.clear()``."""
    return get_retriever()


def _init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_keys" not in st.session_state:
        st.session_state.uploaded_keys = set()


def _render_sidebar() -> None:
    with st.sidebar:
        st.header(i18n.t("sidebar_docs"))

        uploads = st.file_uploader(
            i18n.t("upload_label"),
            type=[extension.lstrip(".") for extension in config.SUPPORTED_EXTENSIONS],
            accept_multiple_files=True,
        )
        if uploads:
            fresh = [
                item for item in uploads
                if (item.name, item.size) not in st.session_state.uploaded_keys
            ]
            if fresh:
                for item in fresh:
                    save_uploaded_file(item.name, item.getbuffer())
                    st.session_state.uploaded_keys.add((item.name, item.size))
                st.success(i18n.t("upload_success"))
                st.rerun()
        st.caption(i18n.t("upload_hint"))

        documents = list_documents()
        if not documents:
            st.caption(i18n.t("docs_empty"))
        else:
            for index, document in enumerate(documents):
                columns = st.columns([4, 1])
                columns[0].caption(document["name"])
                if columns[1].button(
                    i18n.t("doc_delete"), key=f"delete_{index}_{document['name']}"
                ):
                    delete_document(document["name"])
                    cached_retriever.clear()
                    st.rerun()

        if st.button(i18n.t("rebuild_index"), type="primary"):
            with st.spinner(i18n.t("thinking")):
                try:
                    build_index()
                    cached_retriever.clear()
                    st.success(i18n.t("rebuild_success"))
                except Exception as exc:
                    st.error(f"{i18n.t('upload_failed')}{exc}")

        if st.button(i18n.t("clear_chat")):
            st.session_state.messages = []
            st.rerun()


def chat_page() -> None:
    _init_state()
    st.title(i18n.t("chat_title"))
    st.caption(i18n.t("chat_subtitle"))
    _render_sidebar()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(i18n.t("chat_placeholder"))
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        buffer = ""

        def on_delta(chunk: str) -> None:
            nonlocal buffer
            buffer += chunk
            placeholder.markdown(buffer + "▌")

        info = run_chat_stream(
            question,
            history=st.session_state.messages[:-1],
            retriever=cached_retriever(),
            on_delta=on_delta,
        )
        placeholder.markdown(info["answer"])

        if info["sources"]:
            st.markdown(f"**{i18n.t('sources_title')}**")
            for source in info["sources"]:
                suffix = (
                    i18n.t("source_page").format(page=source["page"])
                    if source["page"]
                    else ""
                )
                st.caption(f"- {source['file_name']} {suffix}".rstrip())

    st.session_state.messages.append({"role": "assistant", "content": info["answer"]})
    st.session_state.messages = st.session_state.messages[-config.HISTORY_ROUNDS * 2 :]

    write_log(
        question=question,
        called_kb=info["called_kb"],
        sources=info["sources"],
        model=info["model"],
        prompt_tokens=info["prompt_tokens"],
        completion_tokens=info["completion_tokens"],
        total_tokens=info["total_tokens"],
        latency_ms=info["latency_ms"],
        is_unknown=info["is_unknown"],
    )


navigation = st.navigation(
    [
        st.Page(chat_page, title=i18n.t("nav_chat")),
        st.Page(render_admin_page, title=i18n.t("nav_admin")),
    ]
)
navigation.run()
