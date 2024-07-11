# -*- coding: utf-8 -*-
"""
@file    : hf.py
@date    : 2024-07-11
@author  : leafw
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from llm import deepseek

base_url = 'https://huggingface.co'


class Article:
    def __init__(self, title, arxiv_link, abstract):
        self.title = title
        self.arxiv_link = arxiv_link
        self.abstract = abstract


def en_content(article: Article):
    return f"""
## {article.title}
![{article.title}]({article.arxiv_link})
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
    soup = BeautifulSoup(html_content, 'html.parser')

    articles = soup.find_all('article')

    article_list = []
    for article in articles:
        title = article.find('h3').get_text(strip=True)
        link = article.find('a')['href']
        leading_nones = article.find_all('div', class_='leading-none')
        likes_div = None
        for item in leading_nones:
            if item.get('class') == ['leading-none']:
                likes_div = item
                break
        likes = int(likes_div.get_text(strip=True))

        print(f"Title: {title}")
        print(f"Link: {link}")
        print(f"Likes: {likes}")
        print("------")
        if likes < 25:
            continue
        one = {'title': title, 'link': base_url + link, 'likes': likes}
        article_list.append(one)
    return article_list


def parse_article(url, title):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    article_content = soup.find('p', class_='text-gray-700 dark:text-gray-400')
    content = article_content.get_text(strip=True)
    arxiv_link = soup.find('a', class_='btn inline-flex h-9 items-center')['href']

    return Article(title, arxiv_link, content)


def weekly_get():
    # 获取当前日期
    today = datetime.today()

    # 计算当前周的周一日期
    start_of_week = today - timedelta(days=today.weekday())

    # 创建一个包含周一到周五日期的列表
    weekdays = [start_of_week + timedelta(days=i) for i in range(5)]
    return [day.strftime('%Y-%m-%d') for day in weekdays]


def weekly_paper(output_path=''):
    days = weekly_get()
    if output_path == '':
        output_path = days[0].replace('-', '') + '-' + days[-1].replace('-', '') + '.md'
    # 这一份是防止翻译不太好或者其他问题先留存下
    en_articles_content = []
    with open('output.md', 'w') as en:
        for day in days:
            print(f'开始处理日期: {day}')
            url = base_url + '/papers?date=' + day
            article_list = home_parse(url)
            print(f'{day} 主页解析完毕')
            for item in article_list:
                print(f'解析文章{item["title"]}开始')
                article = parse_article(item['link'], item['title'])
                content = en_content(article)
                en_articles_content.append(content)
                en.write(content)
                print(f'解析文章{item["title"]}完毕')
            print(f'日期 {day} 处理结束')
    print('英文输出完毕')
    # 我只要这个
    with open(output_path, 'w') as f:
        for en_article in en_articles_content:
            zh = deepseek.translate_en_zh(en_article)
            f.write(zh + '\n\n')

