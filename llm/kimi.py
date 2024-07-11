# -*- coding: utf-8 -*-
"""
@file    : kimi.py
@date    : 2024-07-11
@author  : leafw
"""

from pathlib import Path
from openai import OpenAI
import os
import prompt_template

kimi_key = os.environ.get('KIMI_KEY')

client = OpenAI(
    api_key=kimi_key,
    base_url="https://api.moonshot.cn/v1",
)


def chat_pdf(message: str, file_content) -> str:
    # 把它放进请求中
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
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
    )
    return completion.choices[0].message.content


def extract_file(file_path: str):
    file_object = client.files.create(file=Path(file_path), purpose="file-extract")
    return client.files.content(file_id=file_object.id).text
