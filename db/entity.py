# -*- coding: utf-8 -*-
"""
@file    : entity.py
@date    : 2024-07-24
@author  : leafw
"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建数据库连接
engine = create_engine('sqlite:///example.db', echo=True)

# 创建基类
Base = declarative_base()


class Paper(Base):
    __tablename__ = 't_paper'
    id = Column(Integer, primary_key=True)
    path = Column(String)
    title = Column(String)
    title_zh = Column(String)
    abstract = Column(String)
    abstract_zh = Column(String)
    authors = Column(String)
    type = Column(String)
    doi = Column(String)
    href = Column(String)
    short_title = Column(String)
    create_time = Column(String)
    update_time = Column(String)


# 创建表（如果表不存在）
Base.metadata.create_all(engine)
#
# # 创建会话工厂
# Session = sessionmaker(bind=engine)
#
# # 创建会话并执行操作（每次操作时）
# session = Session()
#
# # 操作数据示例
# paper = Paper(path='a.pdf', title='title', abstract='abstract', authors='authors')
# session.add(paper)
# session.commit()
# session.close()
