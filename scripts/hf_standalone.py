#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立的HuggingFace论文抓取与翻译脚本
将所有依赖功能整合到一个文件中
"""

import requests
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import arxiv
from urllib.parse import urlparse
from openai import OpenAI
from typing import Optional

# 基础URL
base_url = "https://huggingface.co"

# LLM配置
llm_config = {
    "deepseek": {
        "model_name": "deepseek-chat",
        "api_key": os.environ.get("DEEPSEEK_KEY"),
        "base_url": "https://api.deepseek.com",
    }
}

# 翻译提示词模板
en_zh_prompt = """
你是一位精通简体中文的专业翻译，尤其擅长将英文的专业学术论文或文章翻译成面向专业技术人员的中文技术文章。请你帮我将以下英文段落翻译成中文，风格与中文理工技术书籍读物相似。

规则：
- 翻译时要准确传达原文的事实和背景。
- 即使上意译也要保留原始段落格式，以及保留术语，例如 FLAC，JPEG 等。保留公司缩写，例如 Microsoft, Amazon, OpenAI 等。
- 人名不翻译
- 同时要保留引用的论文，例如 [20] 这样的引用。
- 对于 Figure 和 Table，翻译的同时保留原有格式，例如："Figure 1: "翻译为"图 1: "，"Table 1: "翻译为："表 1: "。
- 全角括号换成半角括号，并在左括号前面加半角空格，右括号后面加半角空格。
- 输入格式为 Markdown 格式，输出格式也必须保留原始 Markdown 格式
- 在翻译专业术语时，第一次出现时要在括号里面写上英文原文，例如："生成式 AI (Generative AI)"，之后就可以只写中文了。
- 注意你翻译内容的受众是专业技术人员，因此不需要对专业术语做口语化的解释。
- 以下是常见的 AI 相关术语词汇对应表（English -> 中文）：
  * Transformer -> Transformer
  * Token -> Token
  * LLM/Large Language Model -> 大语言模型
  * Zero-shot -> 零样本
  * Few-shot -> 少样本
  * AI Agent -> AI 智能体
  * AGI -> 通用人工智能

策略：

分三步进行翻译工作，并打印每步的结果：
1. 根据英文内容直译，保持原有格式，不要遗漏任何信息
2. 根据第一步直译的结果，指出其中存在的具体问题，要准确描述，不宜笼统的表示，也不需要增加原文不存在的内容或格式，包括不仅限于：
  - 不符合中文表达习惯，明确指出不符合的地方
  - 语句不通顺，指出位置，不需要给出修改意见，意译时修复
3. 根据第一步直译的结果和第二步指出的问题，重新进行意译，保证内容的原意的基础上，使其更易于理解，更符合中文的表达习惯，同时保持原有的格式不变

返回格式如下，"{xxx}"表示占位符：

### 直译
{直译结果}

***

### 问题
{直译的具体问题列表}

***

### 意译
```
{意译结果}
```

现在请按照上面的要求从第一行开始翻译以下内容为简体中文：
```
"""

# ArxivData类定义
class ArxivData:
    def __init__(self, file_path: str, arxiv_id: str, title: str, abstract: str, file_id: str = '',
                 title_abstract_cn: str = '', content: str = '', faq=None, chat_history=None):
        self.file_path = file_path
        self.arxiv_id = arxiv_id
        self.title = title
        self.abstract = abstract
        self.file_id = file_id
        self.title_abstract_cn = title_abstract_cn
        self.content = content
        self.faq = faq if faq is not None else {}
        self.chat_history = chat_history if chat_history is not None else {}

    def to_dict(self):
        return {
            'file_path': self.file_path,
            'arxiv_id': self.arxiv_id,
            'file_id': self.file_id,
            'title': self.title,
            'abstract': self.abstract,
            'title_abstract_cn': self.title_abstract_cn,
            'content': self.content,
            'faq': self.faq,
            'chat_history': self.chat_history
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            file_path=data.get('file_path', ''),
            arxiv_id=data.get('arxiv_id', ''),
            title=data.get('title', ''),
            abstract=data.get('abstract', ''),
            file_id=data.get('file_id', ''),
            title_abstract_cn=data.get('title_abstract_cn', ''),
            content=data.get('content', ''),
            faq=data.get('faq', {}),
            chat_history=data.get('chat_history', {})
        )


# LLM基类
class LLM:
    def __init__(self, model_name: str):
        conf = llm_config.get(model_name)
        if conf is None:
            # 如果没有配置，使用默认配置
            conf = {
                "model_name": model_name,
                "api_key": "",
                "base_url": "http://127.0.0.1:11434",
            }
        self.model_name = conf["model_name"]
        self.api_key = conf["api_key"]
        self.base_url = conf["base_url"]
        self.client = None

        # 只有当API key存在时才创建OpenAI客户端
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)


# OpenAI LLM实现
class OpenAiLlm(LLM):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, message: str, system_prompt: str = "", history=None, stream=False):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=stream,
        )

        if stream:
            return response
        else:
            return response.choices[0].message.content


# Agent基类
class Agent:
    def __init__(self, llm: LLM, desc: str = ""):
        self.llm = llm
        self.desc = desc

    def run(self, **kwargs):
        pass


# 翻译Agent
class TranslaterAgent(Agent):
    def __init__(self, llm: LLM):
        super().__init__(llm, "翻译智能体")

    def run(self, text):
        s = self.llm.chat(text, en_zh_prompt)
        return self.extract_yy_text(s)
    
    def extract_yy_text(self, text):
        # 使用正则表达式匹配 "### 意译" 后面的文本
        pattern = r'### 意译\s*(```)?(.+?)(```)?(?=###|\Z)'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            # 提取匹配的文本，去除可能存在的 ``` 符号
            extracted_text = match.group(2).strip()
            return extracted_text
        else:
            return "未找到意译部分"


# Arxiv客户端
class ArxivClient:
    def __init__(self):
        self.client = arxiv.Client()
    
    def search_by_id(self, arxiv_id: str) -> Optional[ArxivData]:
        # Search for the paper with the given ID
        id_search = arxiv.Search(id_list=[arxiv_id])

        try:
            # 只拿第一个
            result = next(self.client.results(id_search))
            return ArxivData('', arxiv_id, result.title, result.summary)
        except StopIteration:
            # Handle the case where no result is found
            print(f"No paper found with ID {arxiv_id}")
        except Exception as e:
            # Handle other potential exceptions
            print(f"An error occurred: {e}")
        return None

    def search_by_url(self, url: str) -> Optional[ArxivData]:
        parsed_url = urlparse(url)
        # 获取路径的最后一个部分
        arxiv_id = parsed_url.path.split('/')[-1]
        return self.search_by_id(arxiv_id)


# 文章类
class Article:
    def __init__(self, title, arxiv_link, abstract):
        self.title = title
        self.arxiv_link = arxiv_link
        self.abstract = abstract


# 解析HuggingFace首页文章列表
def home_parse(url):
    """
    获取文章列表
    :return:
    """
    response = requests.get(url + "/papers/week/2025-W22")
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


# 生成英文内容
def en_content(title: str, link: str, abstract: str):
    return f"""
## {title}
[{title}]({link})

{abstract}
"""


# 获取英文内容
def get_en_content():
    articles = home_parse(base_url)
    en_contents = []
    arxiv_client = ArxivClient()
    
    with open("output.md", "w") as f:
        for article in articles:
            arxiv_id = article['link'].split('/')[-1]
            paper = arxiv_client.search_by_id(arxiv_id)
            if paper:
                item = en_content(article['title'], 'https://arxiv.org/abs/' + arxiv_id, paper.abstract)
                en_contents.append(item)
                f.write(item + "\n\n")
    return en_contents


# 获取当前周的日期列表
def weekly_get():
    # 获取当前日期
    today = datetime.today()

    # 计算当前周的周一日期
    start_of_week = today - timedelta(days=today.weekday())

    # 创建一个包含周一到周五日期的列表
    weekdays = [start_of_week + timedelta(days=i) for i in range(5)]
    return [day.strftime("%Y-%m-%d") for day in weekdays]


# 主函数
def main():
    # 初始化LLM和翻译Agent
    try:
        deepseek = OpenAiLlm("deepseek")
        trans_agent = TranslaterAgent(deepseek)
        
        # 获取英文文章内容
        en_articles_content = get_en_content()
        print('英文输出完毕')
        
        # 获取当前周的日期
        days = weekly_get()
        output_path = days[0].replace("-", "") + "-" + days[-1].replace("-", "") + ".md"
        
        # 翻译并输出到文件
        with open(output_path, "w") as f:
            for en_article in en_articles_content:
                zh = trans_agent.run(en_article)
                f.write(zh + "\n\n")
        
        print(f"翻译完成，输出文件: {output_path}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == '__main__':
    main()
