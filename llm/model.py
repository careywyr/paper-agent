# -*- coding: utf-8 -*-
"""
@file    : model.py
@date    : 2024-07-22
@author  : leafw
"""
from openai import OpenAI
import requests


class LLM:
    def __init__(self, model_name: str, api_key: str = "", base_url: str = ""):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url

    def chat(self, message: str, system_prompt: str = "") -> str:
        pass


class OpenAiLlm(LLM):
    def __init__(self, model_name: str, api_key: str = "", base_url: str = ""):
        super().__init__(model_name, api_key, base_url)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, message: str, system_prompt: str = "") -> str:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            stream=False
        )
        return response.choices[0].message.content


class OllamaLlm(LLM):
    def __init__(self, model_name: str, api_key: str = "", base_url: str = ""):
        super().__init__(model_name, api_key, base_url)

    def chat(self, message: str, system_prompt: str = "") -> str:
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

        response = requests.post(self.base_url + '/api/chat', json=data)
        return response.json()['message']['content']
