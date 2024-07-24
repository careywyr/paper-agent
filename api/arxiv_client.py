# -*- coding: utf-8 -*-
"""
@file    : arxiv_client.py
@date    : 2024-07-24
@author  : leafw
"""
import arxiv
from db.entity import Paper
from datetime import datetime

# Construct the default API client.
client = arxiv.Client()


def search_by_id(arxiv_id: str) -> Paper | None:
    # Search for the paper with the given ID
    id_search = arxiv.Search(id_list=[arxiv_id])

    try:
        # 只拿第一个
        result = next(client.results(id_search))
        paper = Paper(title=result.title, abstract=result.summary, authors=','.join([a.name for a in result.authors]),
                      href=result.links[0].href, type='arxiv', create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return paper
    except StopIteration:
        # Handle the case where no result is found
        print(f"No paper found with ID {arxiv_id}")
    except Exception as e:
        # Handle other potential exceptions
        print(f"An error occurred: {e}")
    return None


p = search_by_id("2405.16506")
print(p.abstract)
