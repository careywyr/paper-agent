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
        "base_url": "http://localhost:11434",
    },
    "qwen": {
        "model_name": "qwen",
        "api_key": "",
        "base_url": "http://localhost:11434",
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
                "base_url": "http://localhost:11434",
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
                    "content": prompt_template.paper_system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt_template.paper_user_prompt.format(
                        paper_content=file_content, question=message
                    ),
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

    def upload_file(self, file_path: str) -> str:
        """上传文件到Kimi"""
        try:
            with open(file_path, "rb") as file:
                response = self.client.files.create(file=file, purpose="assistants")
                return response.id
        except Exception as e:
            print(f"上传文件失败: {e}")
            return ""

    def extract_file(self, file_id: str) -> str:
        """从Kimi提取文件内容"""
        try:
            response = self.client.files.retrieve_content(file_id=file_id)
            return response.content
        except Exception as e:
            print(f"提取文件内容失败: {e}")
            return ""

    def list_files(self) -> list:
        """列出Kimi上的文件"""
        try:
            response = self.client.files.list()
            return response.data
        except Exception as e:
            print(f"获取文件列表失败: {e}")
            return []

    def remove_file(self, file_id: str) -> bool:
        """从Kimi删除文件"""
        try:
            self.client.files.delete(file_id=file_id)
            return True
        except Exception as e:
            print(f"删除文件失败: {e}")
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
                    "content": prompt_template.paper_system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt_template.paper_user_prompt.format(
                        paper_content=file_content, question=message
                    ),
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
                    "content": prompt_template.paper_system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt_template.paper_user_prompt.format(
                        paper_content=file_content, question=message
                    ),
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
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            print(f"Ollama API调用失败: {e}")
            return ""

    def chat_pdf(self, message: str, file_content) -> str:
        url = f"{self.base_url}/api/chat"

        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": prompt_template.paper_system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt_template.paper_user_prompt.format(
                        paper_content=file_content, question=message
                    ),
                },
            ],
        }

        try:
            response = requests.post(url, json=data)
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
