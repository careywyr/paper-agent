# -*- coding: utf-8 -*-
"""
@file    : utils.py
@date    : 2024-07-13
@author  : leafw
"""
import os
import pymupdf
import re
from pojo import load_Arxiv_data, ArxivData

data_dir = './data'


def ensure_directory_exists(directory_path: str):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"目录 {directory_path} 已创建")
    else:
        print(f"目录 {directory_path} 已存在")


def extract_yy_text(text):
    # 使用正则表达式匹配 "### 意译" 后面的文本
    pattern = r'### 意译\s*(```)?(.+?)(```)?(?=###|\Z)'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        # 提取匹配的文本，去除可能存在的 ``` 符号
        extracted_text = match.group(2).strip()
        return extracted_text
    else:
        return "未找到意译部分"


def read_pdf(file_path: str) -> str:
    doc = pymupdf.open(file_path)
    all_text = []

    for page in doc:
        text = page.get_text()
        all_text.append(text)

    combined_text = "\n".join(all_text)
    return combined_text


def arxiv_dir_path(arxiv_id: str, root_dir: str = data_dir) -> str:
    return root_dir + os.sep + arxiv_id


def get_data_from_arxiv_id(arxiv_id: str) -> ArxivData:
    json_path = arxiv_dir_path(arxiv_id) + os.sep + arxiv_id + '.json'
    return load_Arxiv_data(json_path)