# -*- coding: utf-8 -*-
"""
@file    : model.py
@date    : 2024-07-22
@author  : leafw
"""
from abc import ABC, abstractmethod

from openai import OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
import requests
import prompt_template
import os
from pathlib import Path

llm_config = {
    "deepseek": {
        "model_name": "deepseek-chat",
        "api_key": os.environ.get('DEEPSEEK_KEY'),
        "base_url": "https://api.deepseek.com"
    },
    "kimi": {
        "model_name": "moonshot-v1-128k",
        "api_key": os.environ.get('KIMI_KEY'),
        "base_url": "https://api.moonshot.cn/v1"
    },
    "qwen": {
        "model_name": "qwen2",
        'api_key': '不用填',
        "base_url": "ollama的地址"
    }
}


class LLM(ABC):
    def __init__(self, model_name: str):
        conf = llm_config.get(model_name)
        self.model_name = conf['model_name']
        self.api_key = conf['api_key']
        self.base_url = conf['base_url']

    @abstractmethod
    def chat(self, message: str, system_prompt: str = "", history=None, stream=False) -> str | Stream[ChatCompletionChunk]:
        pass

    @abstractmethod
    def chat_pdf(self, message: str, file_content) -> str:
        pass


class OpenAiLlm(LLM):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, message: str, system_prompt: str = "", history=None, stream=False) -> str | Stream[ChatCompletionChunk]:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=history if history is not None else [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            stream=stream
        )
        if stream:
            return response
        return response.choices[0].message.content

    def chat_pdf(self, message: str, file_content) -> str:
        default_history = [
            {
                "role": "system",
                "content": prompt_template.paper_system
            },
            {
                "role": "system",
                "content": file_content,
            }
        ]
        messages = default_history.copy()
        messages.append({"role": "user", "content": message})

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=False
        )
        res = completion.choices[0].message.content
        return res


class KimiLlm(OpenAiLlm):
    def __init__(self):
        super().__init__('kimi')

    def upload_file(self, file_path: str) -> str:
        file_object = self.client.files.create(file=Path(file_path), purpose="file-extract")
        return file_object.id

    def extract_file(self, file_id: str):
        return self.client.files.content(file_id=file_id).text

    def list_files(self):
        file_list = self.client.files.list()
        # 要用到的应该就俩属性: id, filename
        return file_list.data

    def remove_file(self, file_id: str):
        self.client.files.delete(file_id=file_id)
        print('remove success')


class OllamaLlm(LLM):

    def __init__(self, model_name: str):
        super().__init__(model_name)

    def chat_pdf(self, message: str, file_content) -> str:
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt_template.paper_system},
                {
                    "role": "user",
                    "content": prompt_template.build_paper(file_content, message)
                }
            ],
            "stream": False
        }
        response = requests.post(self.base_url + '/api/chat', json=data)
        return response.json()['message']['content']

    def chat(self, message: str, system_prompt: str = "", history=None, stream=False) -> str:
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": message
                }
            ],
            "stream": stream
        }
        response = requests.post(self.base_url + '/api/chat', json=data)
        res = response.json()['message']['content']
        print(res)
        return res
