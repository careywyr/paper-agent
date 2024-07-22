# -*- coding: utf-8 -*-
"""
@file    : ollama.py
@date    : 2024-07-22
@author  : leafw
"""

import requests

url = "https://85d1-34-83-202-227.ngrok-free.app/api/chat"


def chat(message: str, system_prompt: str = "You are a helpful assistant"):
    data = {
        "model": "qwen2",
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": message
            }
        ],
        "stream": False
    }

    response = requests.post(url, json=data)

    return response.json()['message']['content']


result = chat("为什么天是蓝色的", system_prompt="请你使用中文回答问题")
print(result)
