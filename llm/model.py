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

llm_config = {
    "deepseek": {
        "model_name": "deepseek-chat",
        "api_key": os.environ.get("DEEPSEEK_KEY"),
        "base_url": "https://api.deepseek.com",
    },
    "kimi": {
        "model_name": "moonshot-v1-128k",
        "api_key": os.environ.get("KIMI_KEY"),
        "base_url": "https://api.moonshot.cn/v1",
    },
    "deepseek-r1": {
        "model_name": "deepseek-r1:32b",
        "api_key": "",
        "base_url": "http://127.0.0.1:11434",
    },
    "qwen2.5:32b": {
        "model_name": "qwen2.5:32b",
        "api_key": "",
        "base_url": "http://127.0.0.1:11434",
    },
    "qwen": {
        "model_name": "qwen",
        "api_key": "",
        "base_url": "http://127.0.0.1:11434",
    },
}


class LLM(ABC):
    def __init__(self, model_name: str):
        conf = llm_config.get(model_name)
        if conf is None:
            # 如果没有配置，使用默认配置
            conf = {
                "model_name": model_name,
                "api_key": "",
                "base_url": "http://127.0.0.1:11434",
            }
        self.model_name = conf["model_name"]
        self.api_key = conf["api_key"]
        self.base_url = conf["base_url"]
        self.client = None

        # 只有当API key存在时才创建OpenAI客户端
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    @abstractmethod
    def chat(
        self, message: str, system_prompt: str = "", history=None, stream=False
    ) -> str:
        pass

    @abstractmethod
    def chat_pdf(self, message: str, file_content) -> str:
        pass


class OpenAiLlm(LLM):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    # 检查API连接状态
    def check_connection(self) -> bool:
        try:
            if not self.api_key:
                return False
            self.client.models.list()
            return True
        except Exception as e:
            print(f"连接检查失败: {e}")
            return False

    def chat(
        self, message: str, system_prompt: str = "", history=None, stream=False
    ) -> str | Stream[ChatCompletionChunk]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=stream,
        )

        if stream:
            return response
        else:
            return response.choices[0].message.content

    def chat_pdf(self, message: str, file_content) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": prompt_template.paper_system,
                },
                {
                    "role": "user",
                    "content": prompt_template.build_paper(file_content, message),
                },
            ],
        )
        return response.choices[0].message.content


class KimiLlm(LLM):
    def __init__(self):
        super().__init__("kimi")
        if not self.api_key:
            raise ValueError("Kimi API key is required")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    # 检查Kimi API连接状态
    def check_connection(self) -> bool:
        try:
            if not self.api_key:
                return False
            self.client.models.list()
            return True
        except Exception as e:
            print(f"连接检查失败: {e}")
            return False

    def chat(
        self, message: str, system_prompt: str = "", history=None, stream=False
    ) -> str | Stream[ChatCompletionChunk]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=stream,
        )

        if stream:
            return response
        else:
            return response.choices[0].message.content

    def chat_pdf(self, message: str, file_content) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": prompt_template.paper_system,
                },
                {
                    "role": "user",
                    "content": prompt_template.build_paper(file_content, message),
                },
            ],
        )
        return response.choices[0].message.content


class DeepseekLlm(LLM):
    def __init__(self):
        super().__init__("deepseek")
        if not self.api_key:
            raise ValueError("Deepseek API key is required")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    # 检查Deepseek API连接状态
    def check_connection(self) -> bool:
        try:
            if not self.api_key:
                return False
            self.client.models.list()
            return True
        except Exception as e:
            print(f"连接检查失败: {e}")
            return False

    def chat(
        self, message: str, system_prompt: str = "", history=None, stream=False
    ) -> str | Stream[ChatCompletionChunk]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=stream,
        )

        if stream:
            return response
        else:
            return response.choices[0].message.content

    def chat_pdf(self, message: str, file_content) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": prompt_template.paper_system,
                },
                {
                    "role": "user",
                    "content": prompt_template.build_paper(file_content, message),
                },
            ],
        )
        return response.choices[0].message.content


class OllamaLlm(LLM):
    def __init__(self, model_name: str):
        super().__init__(model_name)

    def chat(
        self, message: str, system_prompt: str = "", history=None, stream=False
    ) -> str:
        url = f"{self.base_url}/api/chat"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        data = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
        }

        try:
            print(data)
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            print(f"Ollama API调用失败: {e}")
            return ""

    def chat_pdf(self, message: str, file_content) -> str:
        url = f"{self.base_url}/api/chat"
        prompt = prompt_template.build_paper(file_content, message)
        print(len(prompt))
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": prompt_template.paper_system,
                },
                {
                    "role": "user",
                    "content": prompt_template.build_paper(file_content, message),
                },
            ],
        }

        try:
            response = requests.post(url, json=data)
            print(response.json())
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            print(f"Ollama API调用失败: {e}")
            return ""

    # 检查与Ollama服务器的连接状态
    def check_connection(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/version")
            return response.status_code == 200
        except Exception as e:
            print(f"连接检查失败: {e}")
            return False

    # 获取可用的模型列表
    def list_models(self) -> list:
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return [model["name"] for model in response.json()["models"]]
            return []
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return []
