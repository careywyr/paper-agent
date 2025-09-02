# -*- coding: utf-8 -*-
"""
@file    : search_tools.py
@date    : 2025-06-30
@author  : leafw
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

import search.arxiv_client as arxiv_client
from concurrent.futures import ThreadPoolExecutor
from llm.model import client
from common.prompt_template import search_rewrite

def search_related(query: str):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": search_rewrite},
            {"role": "user", "content": query}
        ]
    )
    output = response.choices[0].message.content
    
    # 校验格式是否包含**分隔符
    if '**' in output:
        # 按**分割字符串并过滤空字符串
        keywords = [keyword.strip() for keyword in output.split('**') if keyword.strip()]
        print(f"分割后的关键词: {keywords}")
    else:
        print(f"格式不正确，未找到**分隔符。原始输出: {output}")
        keywords = [output.strip()]  # 如果格式不对，将整个字符串作为单个关键词
    # 并发调用搜索，控制并发数为min(len(keywords), 5)
    max_workers = min(len(keywords), 5)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(arxiv_client.search_by_query, keywords))
        for i, result in enumerate(results):
            print(f"关键词 '{keywords[i]}' 的搜索结果:")
            print(result)
            print("-" * 50)

if __name__ == '__main__':
    search_related('PID控制和AI的结合')
