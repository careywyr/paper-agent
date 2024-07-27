# -*- coding: utf-8 -*-
"""
@file    : aminer.py
@date    : 2024-07-24
@author  : leafw
本项目未使用，但是个很有用的网站
"""

import os
import requests

aminer_key = os.environ.get('AMINER_KEY')

# 设置请求头
headers = {
    'Authorization': aminer_key
}


def search(title):
    simple_result = simple_search(title)
    if not simple_result:
        print(f'can not find {title}')
        return
    aminer_paper_id = simple_result['id']
    result = search_by_id(aminer_paper_id)
    return {
        "title": result['title'],
        "abstract": result['abstract']
    }


def simple_search(title):
    url = f'https://datacenter.aminer.cn/gateway/open_platform/api/v3/paper/list/by/publish?page=1&size=10&title={title}'
    # 发送GET请求
    response = requests.get(url, headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        # 请求成功，处理响应数据
        data = response.json()
        if len(data['data']) > 0:
            return data['data'][0]
        return None
    else:
        # 请求失败，打印错误信息
        print(f"Request failed with status code {response.status_code}")
    return None


def search_by_id(aminer_paper_id: str):
    url = f'https://datacenter.aminer.cn/gateway/open_platform/api/v3/paper/platform/details/not/contain/wos/by/id?id={aminer_paper_id}'

    response = requests.get(url, headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        # 请求成功，处理响应数据
        response_data = response.json()
        return response_data['data']
    else:
        # 请求失败，打印错误信息
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None

