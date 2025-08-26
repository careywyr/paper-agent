# -*- coding: utf-8 -*-
"""
@file    : model.py
@date    : 2024-07-22
@author  : leafw
"""

from abc import ABC, abstractmethod

from openai import OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
import prompt_template


class LLM(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.base_url = "http://127.0.0.1:11434/v1"
        self.client = OpenAI(api_key="", base_url=self.base_url)

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
        self.client = OpenAI(api_key="", base_url=self.base_url)

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


