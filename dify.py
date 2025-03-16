# -*- coding: utf-8 -*-
"""
@file    : dify.py
@date    : 2025-03-09
@author  : leafw
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

base_url = "https://huggingface.co"

class Article:
    def __init__(self, title, arxiv_link, abstract):
        self.title = title
        self.arxiv_link = arxiv_link
        self.abstract = abstract


def en_content(article: Article):
    return f"""
## {article.title}
[{article.title}]({article.arxiv_link})

{article.abstract}
"""


def home_parse(url):
    """
    获取文章列表
    :return:
    """
    response = requests.get(url)
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
        if likes < 25:
            break
        print(f"Title: {title}")
        print(f"Link: {link}")
        print(f"Likes: {likes}")
        print("------")
        one = {"title": title, "link": base_url + link, "likes": likes}
        article_list.append(one)
    return article_list


def parse_article(url, title):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    article_content = soup.find("p", class_="text-gray-700 dark:text-gray-400")
    content = article_content.get_text(strip=True)
    arxiv_link = soup.find("a", class_="btn inline-flex h-9 items-center")["href"]

    return Article(title, arxiv_link, content)


def weekly_get():
    # 获取当前日期
    today = datetime.today()

    # 计算当前周的周一日期
    start_of_week = today - timedelta(days=today.weekday())

    # 创建一个包含周一到周五日期的列表
    weekdays = [start_of_week + timedelta(days=i) for i in range(5)]
    return [day.strftime("%Y-%m-%d") for day in weekdays]


days = weekly_get()

en_articles_content = []
for day in days:
    url = base_url + "/papers?date=" + day
    article_list = home_parse(url)
    for item in article_list:
        article = parse_article(item["link"], item["title"])
        content = en_content(article)
        en_articles_content.append(content)
        print(content)