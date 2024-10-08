# -*- coding: utf-8 -*-
"""
@file    : pojo.py
@date    : 2024-07-13
@author  : leafw
"""
import json


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

    def save_to_json(self):
        # 将对象转换为字典
        data_dict = self.to_dict()
        json_path = self.file_path.replace('pdf', 'json')
        # 写入JSON文件
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

        print(f"数据已写入 {json_path}")


def load_Arxiv_data(json_file_path: str) -> ArxivData | None:
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return ArxivData.from_dict(data)
    except FileNotFoundError:
        print(f"文件 {json_file_path} 未找到.")
        return None
