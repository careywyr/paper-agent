# -*- coding: utf-8 -*-
"""
@file    : model_settings.py
@date    : 2024-02-05
@author  : leafw
"""
import streamlit as st
import os
import sys

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from llm.model import KimiLlm, OpenAiLlm, OllamaLlm, DeepseekLlm
from utils.config_manager import ConfigManager

def model_settings(current_llm):
    st.markdown("<h1 style='text-align: center; font-size: 32px;'>模型设置</h1>",
                unsafe_allow_html=True)
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 初始化session state
    if 'active_model' not in st.session_state:
        st.session_state.active_model = config_manager.get('active_model', (
            'kimi' if isinstance(current_llm, KimiLlm)
            else 'deepseek' if isinstance(current_llm, DeepseekLlm)
            else 'ollama' if isinstance(current_llm, OllamaLlm)
            else None
        ))
    
    def save_model_config():
        """保存当前模型配置"""
        config = {
            'active_model': st.session_state.active_model,
            'kimi': {
                'api_key': st.session_state.get('kimi_api_key', ''),
                'api_base': st.session_state.get('kimi_api_base', 'https://api.moonshot.cn/v1'),
                'model': st.session_state.get('kimi_model', 'moonshot-v1-128k')
            },
            'deepseek': {
                'api_key': st.session_state.get('deepseek_api_key', ''),
                'api_base': st.session_state.get('deepseek_api_base', 'https://api.deepseek.com/v1'),
                'model': st.session_state.get('deepseek_model', 'deepseek-chat')
            },
            'ollama': {
                'url': st.session_state.get('ollama_url', 'http://127.0.0.1:11434'),
                'client_verify': st.session_state.get('client_verify', True),
                'models': st.session_state.get('selected_models', [])
            }
        }
        config_manager.update(config)
    
    def load_model_config():
        """加载模型配置"""
        config = config_manager.config
        if config:
            # Kimi配置
            kimi_config = config.get('kimi', {})
            st.session_state.kimi_api_key = kimi_config.get('api_key', '')
            st.session_state.kimi_api_base = kimi_config.get('api_base', 'https://api.moonshot.cn/v1')
            st.session_state.kimi_model = kimi_config.get('model', 'moonshot-v1-128k')
            
            # Deepseek配置
            deepseek_config = config.get('deepseek', {})
            st.session_state.deepseek_api_key = deepseek_config.get('api_key', '')
            st.session_state.deepseek_api_base = deepseek_config.get('api_base', 'https://api.deepseek.com/v1')
            st.session_state.deepseek_model = deepseek_config.get('model', 'deepseek-chat')
            
            # Ollama配置
            ollama_config = config.get('ollama', {})
            st.session_state.ollama_url = ollama_config.get('url', 'http://127.0.0.1:11434')
            st.session_state.client_verify = ollama_config.get('client_verify', True)
            st.session_state.selected_models = ollama_config.get('models', [])
    
    # 首次加载配置
    if 'config_loaded' not in st.session_state:
        load_model_config()
        st.session_state.config_loaded = True
    
    # Kimi设置
    with st.expander("🤖 Kimi", expanded=st.session_state.active_model == 'kimi'):
        col1, col2 = st.columns([6, 1])
        with col2:
            kimi_enabled = st.toggle(
                "启用", 
                value=st.session_state.active_model == 'kimi',
                key="kimi_toggle",
                on_change=lambda: (
                    setattr(st.session_state, 'active_model', 
                           'kimi' if not st.session_state.active_model == 'kimi' else None),
                    save_model_config()
                )
            )
        
        if kimi_enabled:
            with col1:
                st.markdown("### Kimi设置")
            # API Key设置
            kimi_api_key = st.text_input(
                "Kimi API Key",
                value=st.session_state.get('kimi_api_key', ''),
                type="password",
                help="请输入Kimi API Key",
                key="kimi_api_key_input",
                on_change=save_model_config
            )
            if kimi_api_key:
                st.session_state.kimi_api_key = kimi_api_key

            # API代理地址
            kimi_api_base = st.text_input(
                "API代理地址",
                value=st.session_state.get('kimi_api_base', 'https://api.moonshot.cn/v1'),
                help="API代理地址，默认为https://api.moonshot.cn/v1",
                key="kimi_api_base_input",
                on_change=save_model_config
            )
            if kimi_api_base:
                st.session_state.kimi_api_base = kimi_api_base

            # 模型选择
            kimi_models = ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
            selected_kimi_model = st.selectbox(
                "选择模型",
                options=kimi_models,
                index=kimi_models.index(st.session_state.get('kimi_model', 'moonshot-v1-128k')),
                key="kimi_model_select",
                on_change=save_model_config
            )
            st.session_state.kimi_model = selected_kimi_model

            # 连通性检查
            if st.button("检查连通性", key="kimi_check_btn"):
                with st.spinner("正在检查连通性..."):
                    kimi_client = KimiLlm()
                    kimi_client.api_key = kimi_api_key
                    kimi_client.base_url = kimi_api_base
                    if kimi_client.check_connection():
                        st.success("连接成功！")
                    else:
                        st.error("连接失败，请检查API Key和代理地址是否正确")

    # Deepseek设置
    with st.expander("🔍 Deepseek", expanded=st.session_state.active_model == 'deepseek'):
        col1, col2 = st.columns([6, 1])
        with col2:
            deepseek_enabled = st.toggle(
                "启用",
                value=st.session_state.active_model == 'deepseek',
                key="deepseek_toggle",
                on_change=lambda: (
                    setattr(st.session_state, 'active_model',
                           'deepseek' if not st.session_state.active_model == 'deepseek' else None),
                    save_model_config()
                )
            )
        
        if deepseek_enabled:
            with col1:
                st.markdown("### Deepseek设置")
            # API Key设置
            deepseek_api_key = st.text_input(
                "Deepseek API Key",
                value=st.session_state.get('deepseek_api_key', ''),
                type="password",
                help="请输入Deepseek API Key",
                key="deepseek_api_key_input",
                on_change=save_model_config
            )
            if deepseek_api_key:
                st.session_state.deepseek_api_key = deepseek_api_key

            # API代理地址
            deepseek_api_base = st.text_input(
                "API代理地址",
                value=st.session_state.get('deepseek_api_base', 'https://api.deepseek.com/v1'),
                help="API代理地址，默认为https://api.deepseek.com/v1",
                key="deepseek_api_base_input",
                on_change=save_model_config
            )
            if deepseek_api_base:
                st.session_state.deepseek_api_base = deepseek_api_base

            # 模型选择
            deepseek_models = ["deepseek-reasoner", "deepseek-chat"]
            selected_deepseek_model = st.selectbox(
                "选择模型",
                options=deepseek_models,
                index=deepseek_models.index(st.session_state.get('deepseek_model', 'deepseek-chat')),
                key="deepseek_model_select",
                on_change=save_model_config
            )
            if selected_deepseek_model:
                st.session_state.deepseek_model = selected_deepseek_model

            # 连通性检查
            if st.button("检查连通性", key="deepseek_check_btn"):
                with st.spinner("正在检查连通性..."):
                    deepseek_client = DeepseekLlm()
                    deepseek_client.api_key = deepseek_api_key
                    deepseek_client.base_url = deepseek_api_base
                    if deepseek_client.check_connection():
                        st.success("连接成功！")
                    else:
                        st.error("连接失败，请检查API Key和代理地址是否正确")
    
    # Ollama设置
    with st.expander("🦙 Ollama", expanded=st.session_state.active_model == 'ollama'):
        col1, col2 = st.columns([6, 1])
        with col2:
            ollama_enabled = st.toggle(
                "启用",
                value=st.session_state.active_model == 'ollama',
                key="ollama_toggle",
                on_change=lambda: (
                    setattr(st.session_state, 'active_model',
                           'ollama' if not st.session_state.active_model == 'ollama' else None),
                    save_model_config()
                )
            )
        
        if ollama_enabled:
            with col1:
                st.markdown("### Ollama设置")
            # Ollama服务地址
            if 'ollama_url' not in st.session_state:
                st.session_state.ollama_url = "http://127.0.0.1:11434"
            
            ollama_url = st.text_input(
                "Ollama 服务地址",
                value=st.session_state.ollama_url,
                help="必须以http(s)://开头，本地默认端口为11434",
                key="ollama_url_input",
                on_change=save_model_config
            )
            
            if ollama_url != st.session_state.ollama_url:
                st.session_state.ollama_url = ollama_url
            
            # 使用客户端验证模式
            client_verify = st.toggle(
                "使用客户端验证请求模式",
                value=st.session_state.get('client_verify', True),
                help="客户端验证模式会从服务器获取完整会话记录，可提升准确度",
                key="client_verify_toggle",
                on_change=save_model_config
            )
            st.session_state.client_verify = client_verify
            
            # 创建Ollama客户端用于检查连接和获取模型列表
            if 'ollama_client' not in st.session_state:
                st.session_state.ollama_client = OllamaLlm("qwen")
            
            st.session_state.ollama_client.base_url = ollama_url
            
            # 连通性检查按钮
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("检查连通性", key="check_connection_btn"):
                    if st.session_state.ollama_client.check_connection():
                        st.success("连接成功！")
                    else:
                        st.error("连接失败，请检查服务地址是否正确")
            
            with col2:
                if st.button("获取模型列表", key="get_models_btn"):
                    with st.spinner("正在获取模型列表..."):
                        models = st.session_state.ollama_client.list_models()
                        if models:
                            st.session_state.available_models = models
                            st.success(f"获取成功，共找到 {len(models)} 个模型")
                        else:
                            st.error("获取模型列表失败")
            
            # 模型列表
            if 'available_models' not in st.session_state:
                st.session_state.available_models = ["qwen2.5-32b", "deepseek-r1-32b", "qwen2.5-72b"]
            
            if 'selected_models' not in st.session_state:
                st.session_state.selected_models = [st.session_state.available_models[0]] if st.session_state.available_models else []
            
            selected_models = st.multiselect(
                "模型列表",
                options=st.session_state.available_models,
                default=st.session_state.selected_models,
                help="选择要使用的模型",
                key="selected_models",
                on_change=save_model_config
            )
            
            st.markdown("---")
            st.markdown(f"共 {len(selected_models)} 个模型已选择")
