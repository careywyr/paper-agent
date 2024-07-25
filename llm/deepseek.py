# -*- coding: utf-8 -*-
"""
@file    : deepseek.py
@date    : 2024-07-10
@author  : leafw
"""

from openai import OpenAI
import os
import prompt_template
from utils import extract_yy_text

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


def chat_pdf(message: str, file_content) -> str:
    messages = [
        {
            "role": "system",
            "content": prompt_template.paper_system
        },
        {
            "role": "system",
            "content": file_content,
        },
        {"role": "user", "content": message},
    ]

    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.3,
        stream=False
    )
    return completion.choices[0].message.content


def translate_en_zh(text):
    print('执行翻译')
    s = chat(text, prompt_template.en_zh)
    return extract_yy_text(s)


