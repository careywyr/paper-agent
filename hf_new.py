# -*- coding: utf-8 -*-
"""
@file    : hf_new.py
@date    : 2025-03-16
@author  : leafw
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from llm.model import OpenAiLlm
from llm.agent import TranslaterAgent
from api import arxiv_client

base_url = "https://huggingface.co"
deepseek = OpenAiLlm("deepseek")
trans_agent = TranslaterAgent(deepseek)

class Article:
    def __init__(self, title, arxiv_link, abstract):
        self.title = title
        self.arxiv_link = arxiv_link
        self.abstract = abstract





def home_parse(url):
    """
    获取文章列表
    :return:
    """
    response = requests.get(url + "/papers/week/2025-W11")
    html_content = response.text

    # 解析HTML内容
    soup = BeautifulSoup(html_content, "html.parser")

    articles = soup.find_all("article")

    article_list = []
    for article in articles:
        title = article.find("h3").get_text(strip=True)
        link = article.find("a")["href"]
        leading_nones = article.find_all("div", class_="leading-none")
        likes_div = None
        for item in leading_nones:
            if item.get("class") == ["leading-none"]:
                likes_div = item
                break
        likes = int(likes_div.get_text(strip=True))
        if likes < 45:
            break
        print(f"Title: {title}\nLink: {link}\nLikes: {likes}\n------")
        one = {"title": title, "link": base_url + link, "likes": likes}
        article_list.append(one)
    return article_list

def en_content(title: str, link:str, abstract:str):
    return f"""
## {title}
[{title}]({link})

{abstract}
"""


def get_en_content():
    articles = home_parse(base_url)
    en_contents = []
    with open("output.md", "w") as f:
        for article in articles:
            arxiv_id = article['link'].split('/')[-1]
            paper = arxiv_client.search_by_id(arxiv_id)
            item = en_content(article['title'], 'https://arxiv.org/abs/' + arxiv_id, paper.abstract)
            en_contents.append(item)
            f.write(item + "\n\n")
    return en_contents

def weekly_get():
    # 获取当前日期
    today = datetime.today()

    # 计算当前周的周一日期
    start_of_week = today - timedelta(days=today.weekday())

    # 创建一个包含周一到周五日期的列表
    weekdays = [start_of_week + timedelta(days=i) for i in range(5)]
    return [day.strftime("%Y-%m-%d") for day in weekdays]

if __name__ == '__main__':
    en_articles_content = get_en_content()
    print('英文输出完毕')
    days = weekly_get()
    output_path = days[0].replace("-", "") + "-" + days[-1].replace("-", "") + ".md"
    with open(output_path, "w") as f:
        for en_article in en_articles_content:
            zh = trans_agent.run(en_article)
            f.write(zh + "\n\n")
