# -*- coding: utf-8 -*-
"""
@file    : deepseek.py
@date    : 2024-07-10
@author  : leafw
"""

from openai import OpenAI
import os
import prompt_template
import re

deepseek_key = os.environ.get('DEEPSEEK_KEY')
client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")


def chat(message: str, system_prompt: str = "You are a helpful assistant") -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        stream=False
    )

    return response.choices[0].message.content


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


def translate_en_zh(text):
    print('执行翻译')
    s = chat(text, prompt_template.en_zh)
    return extract_yy_text(s)
