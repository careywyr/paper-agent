# -*- coding: utf-8 -*-
"""
@file    : flow.py
@date    : 2024-07-28
@author  : leafw
"""
from urllib.parse import urlparse
from api import arxiv_client
import utils
import os
import requests
from llm.agent import TranslaterAgent
from llm.model import OpenAiLlm
from prompt_template import paper_questions

paper_url = 'https://arxiv.org/abs/2407.18248'

current_llm = OpenAiLlm('deepseek')
trans_agent = TranslaterAgent(current_llm)
md_template_path = 'md_template.md'


def run(url: str):
    parsed_url = urlparse(url)
    arxiv_id = parsed_url.path.split('/')[-1]
    with open(md_template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # 先下载
    url = url.replace("abs", "pdf")
    print(f'开始下载: {url}')
    response = requests.get(url)
    directory_path = utils.arxiv_dir_path(arxiv_id)
    utils.ensure_directory_exists(directory_path)

    file_path = directory_path + os.sep + arxiv_id + '.pdf'

    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"文件下载成功: {file_path}")
    else:
        print(f"文件下载失败，状态码: {response.status_code}")
        return

    # 获取标题和摘要
    arxiv_data = arxiv_client.search_by_id(arxiv_id)
    arxiv_data.file_path = file_path
    arxiv_data.save_to_json()
    print(f'标题和摘要获取成功: {arxiv_data.title}')
    print('开始翻译')

    # 翻译标题和摘要
    content = f'## {arxiv_data.title}\n{arxiv_data.abstract}'
    translated = trans_agent.run(content)
    arxiv_data.title_abstract_cn = translated
    print('翻译结束')

    # 填充问题之外的东西
    template_format = template.format(title=arxiv_data.title, abstract=arxiv_data.abstract, title_abstract_cn=translated)

    # 回答问题
    file_content = utils.read_pdf(arxiv_data.file_path)
    arxiv_data.content = file_content

    for question in paper_questions:
        print(f'回答问题: {question}')
        answer, _ = current_llm.chat_pdf(question, arxiv_data.content)
        arxiv_data.faq[question] = answer
        item = '### ' + question + '\n' + answer + '\n\n'
        template_format += item

    arxiv_data.save_to_json()

    print(f'问题回答结束!')

    with open(arxiv_id + '.md', 'w', encoding='utf-8') as f:
        f.write(template_format)

    print('=============== ending! =============== ')


run(paper_url)



