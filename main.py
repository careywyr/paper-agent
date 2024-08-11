# -*- coding: utf-8 -*-
"""
@file    : arxiv_client.py
@date    : 2024-07-11
@author  : leafw
"""
import requests
import os
import utils
from utils import get_data_from_arxiv_id
from urllib.parse import urlparse
import streamlit as st
from streamlit_option_menu import option_menu
from prompt_template import paper_questions, paper_system
from api import arxiv_client
from llm.model import OpenAiLlm, KimiLlm, OllamaLlm
from llm.agent import TranslaterAgent, PaperAnswerAgent
from front.st_chat import chatting
from front.kimi_file_manage import settings

# 是否使用Kimi
use_kimi = False
# 是否使用ollama
use_ollama = False

data_dir = './data'
md_template_path = 'md_template.md'
current_llm = KimiLlm() if use_kimi else OllamaLlm('qwen') if use_ollama else OpenAiLlm('deepseek')
trans_agent = TranslaterAgent(llm=current_llm)
paper_answer_agent = PaperAnswerAgent(llm=current_llm)


def download(url):
    url = url.replace("abs", "pdf")
    response = requests.get(url)
    last = url.rfind('/')

    arxiv_id = url[last + 1:]
    # 每个论文放在data/arxiv_id文件夹下
    directory_path = utils.arxiv_dir_path(arxiv_id)
    utils.ensure_directory_exists(directory_path)

    file_path = directory_path + os.sep + arxiv_id + '.pdf'

    if os.path.exists(file_path):
        print('文件已经存在')
        return file_path, arxiv_id

    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print("文件下载成功")
    else:
        print(f"文件下载失败，状态码: {response.status_code}")
    return file_path, arxiv_id


def parse_home(url: str) -> dict:
    parsed_url = urlparse(url)
    arxiv_id = parsed_url.path.split('/')[-1]

    arxiv_data = get_data_from_arxiv_id(arxiv_id)
    if arxiv_data:
        return {
            "title": arxiv_data.title,
            "abstract": arxiv_data.abstract,
            "file_path": arxiv_data.file_path,
            "arxiv_id": arxiv_id
        }

    arxiv_data = arxiv_client.search_by_id(arxiv_id)
    # 持久化
    file_path, arxiv_id = download(url)
    arxiv_data.file_path = file_path
    arxiv_data.save_to_json()

    return {
        "title": arxiv_data.title,
        "abstract": arxiv_data.abstract,
        "file_path": file_path,
        "arxiv_id": arxiv_id
    }


def trans(title: str, abstract: str, arxiv_id: str) -> str:
    arxiv_data = get_data_from_arxiv_id(arxiv_id)
    if arxiv_data is None:
        return '系统异常'

    # 如果翻译过就直接拿翻译的
    if arxiv_data.title_abstract_cn is not None and arxiv_data.title_abstract_cn != '':
        return arxiv_data.title_abstract_cn

    content = f'## {title}\n{abstract}'
    translated = trans_agent.run(content)
    arxiv_data.title_abstract_cn = translated
    arxiv_data.save_to_json()
    return translated


def answer_pdf(index: int, file_id: str, arxiv_id: str) -> (str, str):
    arxiv_data = get_data_from_arxiv_id(arxiv_id)
    if arxiv_data is None:
        return '系统异常', '', []

    if arxiv_data.content is None or len(arxiv_data.content) == 0:
        if isinstance(current_llm, KimiLlm):
            file_id = current_llm.upload_file(arxiv_data.file_path)
            file_content = current_llm.extract_file(file_id)
            arxiv_data.file_id = file_id
            arxiv_data.content = file_content
            arxiv_data.save_to_json()
        else:
            file_content = utils.read_pdf(arxiv_data.file_path)
            arxiv_data.content = file_content
            arxiv_data.save_to_json()

    question = paper_questions[index]

    if arxiv_data.faq is not None and arxiv_data.faq.get(question):
        return file_id, arxiv_data.faq.get(question)

    answer = current_llm.chat_pdf(question, arxiv_data.content)
    arxiv_data.faq[question] = answer
    arxiv_data.save_to_json()
    return file_id, answer


def export_md(arxiv_id: str):
    arxiv_data = get_data_from_arxiv_id(arxiv_id)
    path = utils.arxiv_dir_path(arxiv_id)
    with open(md_template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    template_format = template.format(title=arxiv_data.title, abstract=arxiv_data.abstract,
                                      title_abstract_cn=arxiv_data.title_abstract_cn)
    faq = arxiv_data.faq
    for key, value in faq.items():
        item = '### ' + key + '\n' + value + '\n\n'
        template_format += item

    with open(path + os.sep + arxiv_id + '.md', 'w', encoding='utf-8') as f:
        f.write(template_format)

    print('导出结束')


# 定义主页
def home():
    st.markdown("<h1 style='text-align: center; font-size: 32px;'>Arxiv Helper</h1>", unsafe_allow_html=True)

    # 初始化 session state
    if 'responses' not in st.session_state:
        st.session_state.responses = [""] * len(paper_questions)

    if 'title' not in st.session_state:
        st.session_state.title = ""
    if 'abstract' not in st.session_state:
        st.session_state.abstract = ""
    if 'url' not in st.session_state:
        st.session_state.url = ""

    if 'arxiv_id' not in st.session_state:
        st.session_state.arxiv_id = ""
    if 'translated_abstract' not in st.session_state:
        st.session_state.translated_abstract = ""

    if 'file_id' not in st.session_state:
        st.session_state.file_id = ""

    if 'generate_all' not in st.session_state:
        st.session_state.generate_all = False

    if 'generate_index' not in st.session_state:
        st.session_state.generate_index = 0

    url = st.text_input("请输入网址", value=st.session_state.url, key="url_input")

    def analysis_url():
        if st.session_state.url_input:
            analysis_result = parse_home(st.session_state.url_input)
            st.session_state.title = analysis_result['title']
            st.session_state.abstract = analysis_result['abstract']
            st.session_state.arxiv_id = analysis_result['arxiv_id']
            st.rerun()

    if url != st.session_state.url:
        st.session_state.url = url
        analysis_url()

    # 布局分两列
    col1, col2 = st.columns([2, 3])

    with col1:
        if st.session_state.title:
            st.markdown(f"**<h2 style='font-size: 24px;'>标题</h2>** {st.session_state.title}", unsafe_allow_html=True)
            st.markdown(f"**<h3 style='font-size: 20px;'>摘要</h3>** {st.session_state.abstract}",
                        unsafe_allow_html=True)

            if st.button("翻译"):
                with st.spinner("翻译中，请稍候..."):
                    st.session_state.translated_abstract = trans(st.session_state.title, st.session_state.abstract,
                                                                 st.session_state.arxiv_id)
                st.rerun()

            if st.session_state.translated_abstract:
                st.markdown(f"**<h3 style='font-size: 20px;'>翻译结果</h3>** {st.session_state.translated_abstract}",
                            unsafe_allow_html=True)

    with col2:
        if st.session_state.title:
            spinner_placeholder = st.empty()
            b1, b2 = st.columns(2)
            with b1:
                if st.button("生成所有"):
                    st.session_state.generate_all = True
                    st.session_state.generate_index = 0
            with b2:
                if st.button("导出MD"):
                    with st.spinner("导出中，请稍候..."):
                        export_md(st.session_state.arxiv_id)
                        st.rerun()

            for i, question in enumerate(paper_questions):
                with st.form(key=f"form_{i}"):
                    st.markdown(f"**{question}**", unsafe_allow_html=True)
                    st.markdown(f"{st.session_state.responses[i]}", unsafe_allow_html=True)
                    submitted = st.form_submit_button("生成")
                    if submitted:
                        with st.spinner("生成中，请稍候..."):
                            _, result = answer_pdf(i, st.session_state.file_id,
                                                   st.session_state.arxiv_id)
                            st.session_state.responses[i] = result
                            st.rerun()

    # 处理生成所有的问题
    if st.session_state.generate_all and st.session_state.generate_index < len(paper_questions):
        i = st.session_state.generate_index
        with spinner_placeholder.container():
            with st.spinner(f"正在生成问题 {i + 1}/{len(paper_questions)}..."):
                _, result = answer_pdf(i, st.session_state.file_id, st.session_state.arxiv_id)
                st.session_state.responses[i] = result
                st.session_state.generate_index += 1
                if st.session_state.generate_index >= len(paper_questions):
                    st.session_state.generate_all = False
        st.rerun()


# 主函数
def main():
    st.set_page_config(layout="wide")

    options = ["主页", "聊天", "设置"]
    with st.sidebar:
        selected = option_menu(
            menu_title="菜单",  # 菜单标题
            options=options,  # 菜单选项
            icons=["house", "robot", "gear"],  # 菜单图标
            menu_icon="cast",  # 菜单图标
            default_index=0,  # 默认选中菜单项
            orientation="vertical",  # 菜单方向
        )
    if selected == '主页':
        home()
    elif selected == '聊天':
        chatting(st.session_state.arxiv_id if 'arxiv_id' in st.session_state else '')
    elif selected == '设置':
        settings(current_llm)


if __name__ == "__main__":
    main()
