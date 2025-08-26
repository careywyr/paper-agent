# -*- coding: utf-8 -*-
"""
@file    : embed_tools.py
@date    : 2025-06-30
@author  : leafw
"""

from openai import OpenAI

BASE_URL = "http://127.0.0.1:11434/v1"

def embedding_model(model="bge-m3:latest", input="hello world"):
    client = OpenAI(api_key="", base_url=BASE_URL)
    return client.embeddings.create(model=model, input=input)


def chunk_and_embed():
    pass