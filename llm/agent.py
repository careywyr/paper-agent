# -*- coding: utf-8 -*-
"""
@file    : agent.py
@date    : 2024-07-22
@author  : leafw
"""
from llm.model import LLM
import prompt_template
import utils


class Agent:
    def __init__(self, llm: LLM, desc: str = ""):
        self.llm = llm
        self.desc = desc

    def run(self, **kwargs):
        pass


class TranslaterAgent(Agent):
    def __init__(self, llm: LLM):
        super().__init__(llm, "翻译智能体")

    def run(self, text):
        s = self.llm.chat(text, prompt_template.en_zh)
        return utils.extract_yy_text(s)


class PaperAnswerAgent(Agent):
    def __init__(self, llm: LLM):
        super().__init__(llm, "Paper 问答")

    def run(self, question, file_content):
        return self.llm.chat_pdf(question, file_content)
