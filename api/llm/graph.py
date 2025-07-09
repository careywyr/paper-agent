# -*- coding: utf-8 -*-
"""
@file    : graph.py
@date    : 2025-06-30
@author  : leafw
"""

from typing import List, Dict, Optional
from langgraph.graph import StateGraph
from tools import (load_pdf, chunk_and_embed,
                   search_related, summarize_paper,
                   review_outline, make_slides)
from typing import TypedDict

class PaperState(TypedDict):
    request: str                  # 用户输入（DOI / 问题）
    pdf_path: Optional[str] = None
    metadata: Optional[Dict] = None
    chunks: Optional[List[str]] = None
    vector_ids: Optional[List[str]] = None
    related_papers: Optional[List[Dict]] = None
    outline: Optional[str] = None
    review_comments: Optional[str] = None
    slides_path: Optional[str] = None



graph = StateGraph(state_schema=PaperState)

# --- 串行节点 ---
graph.add_node("loader",    load_pdf)
graph.add_node("summarizer", summarize_paper)
graph.add_node("reviewer",   review_outline)
graph.add_node("presenter",  make_slides)

# --- 并行节点 ---
graph.add_node("chunker",   chunk_and_embed)
graph.add_node("searcher",  search_related)

# --- 边 ---
graph.set_entry_point("loader")
# 添加边连接节点
graph.add_edge("loader", "chunker")   # 连接到第一个并行节点
graph.add_edge("loader", "searcher")   # 连接到第二个并行节点

# 设置条件，当 chunker 和 searcher 都完成时，进入 summarizer


def when_both_complete(state):
    # 检查 chunker 和 searcher 是否都已完成
    if state.get("chunks") is not None and state.get("related_papers") is not None:
        return "summarizer"
    return None

graph.add_conditional_edges("chunker", when_both_complete)
graph.add_conditional_edges("searcher", when_both_complete)

# 添加其他边
graph.add_edge("summarizer", "reviewer")   # 质检
graph.add_edge("reviewer", "presenter")    # 生成 PPT
graph.set_finish_point("presenter")
graph.save_graphviz("topology.svg")  # 保存拓扑图
paper_agent = graph.compile()