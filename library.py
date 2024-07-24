# -*- coding: utf-8 -*-
"""
@file    : library.py
@date    : 2024-07-24
@author  : leafw
论文仓库
"""
import pymupdf

doc = pymupdf.open("/Users/carey/Documents/workspace2024/paper-agent/Qu 等 - 2024 - Tool Learning with Large Language Models A Survey.pdf")
for page in doc:
  text = page.get_text()
  print(text)


