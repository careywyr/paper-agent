# -*- coding: utf-8 -*-
"""
@file    : main.py
@date    : 2024-07-10
@author  : leafw
"""

import gradio as gr
import deepseek


# 模拟翻译函数
def trans(text: str) -> str:
    return deepseek.translate_en_zh(text)


# 添加文本框的函数
def add_textbox(text_list):
    text_list.append("")
    return text_list, text_list


# 翻译文本的函数
def translate(text_list):
    translated_list = [trans(text) for text in text_list]
    return text_list, translated_list


# 初始化文本框列表
text_list = [""]
