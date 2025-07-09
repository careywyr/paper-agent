# -*- coding: utf-8 -*-
"""
@file    : graph.py
@date    : 2025-06-05
@author  : leafw
"""

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# 设置环境变量

def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

def create_ollama_model(model_name="qwen3:30b-a3b-fp16"):
    model = ChatOpenAI(
        model_name=model_name,
        openai_api_key="ollama",  # 不需要API密钥
        openai_api_base="http://127.0.0.1:11434/v1",  # Ollama的OpenAI兼容端点
        temperature=0.7
    )
    
    return model

agent = create_react_agent(
    model=create_ollama_model(),  
    tools=[get_weather],  
    prompt="你是一个有帮助的助手"  
)

# 运行agent
def run_agent(query):
    return agent.invoke(
        {"messages": [{"role": "user", "content": query}]}
    )

if __name__ == "__main__":
    print(run_agent("what is the weather in sf"))
