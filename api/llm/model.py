# -*- coding: utf-8 -*-
"""
@file    : model.py
@date    : 2024-07-22
@author  : leafw
"""

from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("DEEPSEEK_KEY"), base_url="https://api.deepseek.com")


