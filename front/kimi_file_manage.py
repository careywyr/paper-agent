# -*- coding: utf-8 -*-
"""
@file    : kimi_file_manage.py
@date    : 2024-08-11
@author  : leafw
"""
import streamlit as st
import pandas as pd
from llm.model import KimiLlm


# 定义设置页面
def settings(current_llm: KimiLlm):
    st.markdown("<h1 style='text-align: center; font-size: 32px;'>Kimi文件管理(存在Kimi才可使用)</h1>",
                unsafe_allow_html=True)

    files = current_llm.list_files()
    df = create_files_dataframe(files)

    # 显示文件表格
    for index, row in df.iterrows():
        col1, col2, col3 = st.columns([3, 7, 2])
        col1.write(row["ID"])
        col2.write(row["FileName"])
        button_placeholder = col3.empty()
        if button_placeholder.button("删除", key=row["ID"]):
            current_llm.remove_file(row["ID"])
            st.rerun()


# 创建显示文件列表的 DataFrame
def create_files_dataframe(files):
    data = {
        "ID": [file.id for file in files],
        "FileName": [file.filename for file in files]
    }
    df = pd.DataFrame(data)
    return df
