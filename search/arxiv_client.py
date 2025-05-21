# -*- coding: utf-8 -*-
"""
@file    : arxiv_client.py
@date    : 2024-07-24
@author  : leafw
"""
import arxiv
from urllib.parse import urlparse
from pojo import ArxivData


# Construct the default API client.
client = arxiv.Client()


def search_by_id(arxiv_id: str) -> ArxivData | None:
    # Search for the paper with the given ID
    id_search = arxiv.Search(id_list=[arxiv_id])

    try:
        # 只拿第一个
        result = next(client.results(id_search))
        return ArxivData('', arxiv_id, result.title, result.summary)
    except StopIteration:
        # Handle the case where no result is found
        print(f"No paper found with ID {arxiv_id}")
    except Exception as e:
        # Handle other potential exceptions
        print(f"An error occurred: {e}")
    return None


def search_by_url(url: str) -> ArxivData | None:
    parsed_url = urlparse(url)
    # 获取路径的最后一个部分
    arxiv_id = parsed_url.path.split('/')[-1]
    return search_by_id(arxiv_id)

