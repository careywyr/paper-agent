# -*- coding: utf-8 -*-
"""
@file    : arxiv_client.py
@date    : 2024-07-11
@author  : leafw
"""
import requests

import pojo
from llm import kimi, deepseek
from prompt_template import paper_questions
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import os
import utils
from pojo import ArxivData
from api import arxiv_client

data_dir = './data'


def arxiv_dir_path(arxiv_id: str):
    return data_dir + os.sep + arxiv_id


def get_data_from_arxiv_id(arxiv_id: str) -> ArxivData:
    json_path = arxiv_dir_path(arxiv_id) + os.sep + arxiv_id + '.json'
    return pojo.load_Arxiv_data(json_path)


def download(url):
    url = url.replace("abs", "pdf")
    response = requests.get(url)
    last = url.rfind('/')

    arxiv_id = url[last + 1:]
    # 每个论文放在data/arxiv_id文件夹下
    directory_path = arxiv_dir_path(arxiv_id)
    utils.ensure_directory_exists(directory_path)

    file_path = directory_path + os.sep + arxiv_id + '.pdf'

    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print("文件下载成功")
    else:
        print(f"文件下载失败，状态码: {response.status_code}")
    return file_path, arxiv_id


def parse_home(url: str) -> dict:
    arxiv_data = arxiv_client.search_by_url(url)

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
    translated = deepseek.translate_en_zh(content)
    arxiv_data.title_abstract_cn = translated
    arxiv_data.save_to_json()
    return translated


def chat_not_kimi(index: int, file_id: str, file_path: str, arxiv_id: str) -> (str, str):
    arxiv_data = get_data_from_arxiv_id(arxiv_id)
    if arxiv_data is None:
        return '系统异常'
    if arxiv_data.content is None or len(arxiv_data.content) == 0:
        file_content = utils.read_pdf(arxiv_data.file_path)
        arxiv_data.content = file_content
        arxiv_data.save_to_json()
    question = paper_questions[index]
    if arxiv_data.faq is not None and arxiv_data.faq.get(question):
        return file_id, arxiv_data.faq.get(question)
    answer = deepseek.chat_pdf(question, arxiv_data.content)
    print(answer)
    arxiv_data.faq[question] = answer
    arxiv_data.save_to_json()
    return file_id, answer


def chat_by_kimi(index: int, file_id: str, file_path: str, arxiv_id: str) -> (str, str):
    arxiv_data = get_data_from_arxiv_id(arxiv_id)
    if arxiv_data is None:
        return '系统异常'

    if file_id is None or file_id == '':
        file_id = kimi.upload_file(file_path)
        file_content = kimi.extract_file(file_id)
        arxiv_data.file_id = file_id
        arxiv_data.content = file_content
        arxiv_data.save_to_json()

    question = paper_questions[index]
    if arxiv_data.faq is not None and arxiv_data.faq.get(question):
        return file_id, arxiv_data.faq.get(question)

    answer = kimi.chat_pdf(question, arxiv_data.content)
    print(answer)
    arxiv_data.faq[question] = answer
    arxiv_data.save_to_json()
    return file_id, answer


# 创建显示文件列表的 DataFrame
def create_files_dataframe(files):
    data = {
        "ID": [file.id for file in files],
        "FileName": [file.filename for file in files]
    }
    df = pd.DataFrame(data)
    return df


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
    if 'file_path' not in st.session_state:
        st.session_state.file_path = ""
    if 'translated_abstract' not in st.session_state:
        st.session_state.translated_abstract = ""

    if 'file_id' not in st.session_state:
        st.session_state.file_id = ""

    url = st.text_input("请输入网址", value=st.session_state.url, key="url_input")

    def analysis_url():
        if st.session_state.url_input:
            analysis_result = parse_home(st.session_state.url_input)
            st.session_state.title = analysis_result['title']
            st.session_state.abstract = analysis_result['abstract']
            st.session_state.arxiv_id = analysis_result['arxiv_id']
            st.session_state.file_path = analysis_result['file_path']
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
        if st.session_state.url:
            for i, question in enumerate(paper_questions):
                with st.form(key=f"form_{i}"):
                    st.markdown(f"**{question}**", unsafe_allow_html=True)
                    st.markdown(f"{st.session_state.responses[i]}", unsafe_allow_html=True)
                    submitted = st.form_submit_button("生成")
                    if submitted:
                        with st.spinner("生成中，请稍候..."):
                            _, result = chat_not_kimi(i, st.session_state.file_id, st.session_state.file_path,
                                                     st.session_state.arxiv_id)
                            st.session_state.responses[i] = result
                            st.rerun()


# 定义设置页面
def settings():
    st.markdown("<h1 style='text-align: center; font-size: 32px;'>Kimi文件管理</h1>", unsafe_allow_html=True)

    files = kimi.list_files()
    df = create_files_dataframe(files)

    # 显示文件表格
    for index, row in df.iterrows():
        col1, col2, col3 = st.columns([3, 7, 2])
        col1.write(row["ID"])
        col2.write(row["FileName"])
        button_placeholder = col3.empty()
        if button_placeholder.button("删除", key=row["ID"]):
            kimi.remove_file(row["ID"])
            st.rerun()


# 主函数
def main():
    st.set_page_config(layout="wide")
    with st.sidebar:
        selected = option_menu(
            menu_title="菜单",  # 菜单标题
            options=["主页", "设置"],  # 菜单选项
            icons=["house", "gear"],  # 菜单图标
            menu_icon="cast",  # 菜单图标
            default_index=0,  # 默认选中菜单项
            orientation="vertical",  # 菜单方向
        )

    if selected == "主页":
        home()
    elif selected == "设置":
        settings()


if __name__ == "__main__":
    main()
