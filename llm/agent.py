# -*- coding: utf-8 -*-
"""
@file    : agent.py
@date    : 2024-07-22
@author  : leafw
"""
from llm.model import LLM
import re
import prompt_template


class Agent:
    def __init__(self, llm: LLM, desc: str = ""):
        self.llm = llm
        self.desc = desc

    def run(self):
        pass


class TranslaterAgent(Agent):
    def __init__(self, llm: LLM):
        super().__init__(llm, "翻译智能体")

    def translate_en_zh(self, text):
        s = self.llm.chat(text, prompt_template.en_zh)
        return extract_yy_text(s)


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