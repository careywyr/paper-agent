# -*- coding: utf-8 -*-
"""
@file    : st_chat.py
@date    : 2024-08-11
@author  : leafw
"""
import streamlit as st
from llm.model import OpenAiLlm
from utils import get_data_from_arxiv_id
from prompt_template import paper_system


# 初始化OpenAiLlm
current_llm = OpenAiLlm('deepseek')


def chatting(arxiv_id):
    st.markdown("<h1 style='text-align: center; font-size: 32px;'>Chat with LLM</h1>",
                unsafe_allow_html=True)
    if 'history' not in st.session_state:
        st.session_state.history = []
    if arxiv_id == '':
        return

    arxiv_data = get_data_from_arxiv_id(arxiv_id)
    if not arxiv_data:
        st.session_state.history = []
    else:
        default_history = [
            {
                "role": "system",
                "content": paper_system
            },
            {
                "role": "system",
                "content": arxiv_data.content,
            }
        ]

        if len(arxiv_data.chat_history) > 0:
            st.session_state.history = arxiv_data.chat_history

        # 说明还没聊过
        if len(arxiv_data.chat_history) == 0:
            st.session_state.history = default_history

        # 这里加上小于等于2是如果曾经聊过天，就不再把这里的东西再重复拼上去了
        if arxiv_data.faq and len(arxiv_data.faq) > 0 and len(st.session_state.history) <= 2:
            for q, a in arxiv_data.faq.items():
                user_msg = {'role': 'user', 'content': q}
                assistant_msg = {'role': 'assistant', 'content': a}
                st.session_state.history.append(user_msg)
                st.session_state.history.append(assistant_msg)

    for message in st.session_state.history:
        if message['role'] == 'system':
            continue
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(message['content'])
        else:
            with st.chat_message("assistant"):
                st.markdown(message['content'])

    # 用户输入
    user_input = st.chat_input(placeholder="", key="input_box")

    if user_input:
        # 保存用户输入到对话历史
        st.session_state.history.append({"role": "user", "content": user_input})
        arxiv_data.chat_history = st.session_state.history
        arxiv_data.save_to_json()

        with st.chat_message("user"):
            st.markdown(user_input)

        ai_reply = current_llm.chat(user_input, history=st.session_state.history, stream=True)
        # 显示AI回复并将其存储到字符串中
        with st.chat_message("assistant"):
            complete_response = st.write_stream(ai_reply)

        st.session_state.history.append({"role": "assistant", "content": complete_response})
        arxiv_data.chat_history = st.session_state.history
        arxiv_data.save_to_json()


