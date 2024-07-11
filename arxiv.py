# -*- coding: utf-8 -*-
"""
@file    : arxiv.py
@date    : 2024-07-11
@author  : leafw
"""
import requests
from llm import kimi
from prompt_template import paper_questions


def download(url):
    response = requests.get(url)
    last_slash_index = url.rfind('/')
    filename = url[last_slash_index + 1:] + '.pdf'
    # 检查请求是否成功
    if response.status_code == 200:
        # 以二进制写入模式打开文件
        with open(filename, 'wb') as file:
            file.write(response.content)
        print("文件下载成功")
    else:
        print(f"文件下载失败，状态码: {response.status_code}")
    return filename


def analysis(pdf_path: str):
    local_path = download(pdf_path)
    file = kimi.extract_file(local_path)
    qa = []
    for question in paper_questions:
        print(question)
        answer = kimi.chat_pdf(question, file)
        print(answer)
        qa.append((question, answer))
    return qa

