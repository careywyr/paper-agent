# -*- coding: utf-8 -*-
"""
@file    : test.py
@date    : 2024-08-11
@author  : leafw
"""
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get('DEEPSEEK_KEY'), base_url="https://api.deepseek.com")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "you are a helpful assistant"},
        {"role": "user", "content": "你好"},
    ],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")