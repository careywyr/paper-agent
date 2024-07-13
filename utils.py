# -*- coding: utf-8 -*-
"""
@file    : utils.py
@date    : 2024-07-13
@author  : leafw
"""
import os


def ensure_directory_exists(directory_path: str):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"目录 {directory_path} 已创建")
    else:
        print(f"目录 {directory_path} 已存在")