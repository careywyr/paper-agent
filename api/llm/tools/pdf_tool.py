# -*- coding: utf-8 -*-
"""
@file    : pdf_tool.py
@date    : 2025-07-15
@author  : leafw
"""


def parse_pdf(pdf_path: str, output_dir: str = None, lang_list: list = None, backend: str = None,
            parse_method: str = None, formula_enable: bool = None, table_enable: bool = None,
            server_url: str = None, return_md: bool = None, return_middle_json: bool = None,
            return_model_output: bool = None, return_content_list: bool = None,
            return_images: bool = None, start_page_id: int = None, end_page_id: int = None) -> str:
    """
    通过调用HTTP接口解析PDF文件
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
        lang_list: 语言列表
        backend: 后端类型
        parse_method: 解析方法
        formula_enable: 是否启用公式解析
        table_enable: 是否启用表格解析
        server_url: 服务器URL
        return_md: 是否返回markdown
        return_middle_json: 是否返回中间JSON
        return_model_output: 是否返回模型输出
        return_content_list: 是否返回内容列表
        return_images: 是否返回图片
        start_page_id: 开始页ID
        end_page_id: 结束页ID
        
    Returns:
        解析结果
    """
    import requests
    import os
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    # 准备请求URL
    url = "http://127.0.0.1:8000/file_parse"
    
    # 准备文件
    files = {
        'files': (os.path.basename(pdf_path), open(pdf_path, 'rb'), 'application/pdf')
    }
    
    # 准备表单数据
    form_data = {}
    if output_dir is not None:
        form_data['output_dir'] = output_dir
    if lang_list is not None:
        form_data['lang_list'] = lang_list
    if backend is not None:
        form_data['backend'] = backend
    if parse_method is not None:
        form_data['parse_method'] = parse_method
    if formula_enable is not None:
        form_data['formula_enable'] = str(formula_enable).lower()
    if table_enable is not None:
        form_data['table_enable'] = str(table_enable).lower()
    if server_url is not None:
        form_data['server_url'] = server_url
    if return_md is not None:
        form_data['return_md'] = str(return_md).lower()
    if return_middle_json is not None:
        form_data['return_middle_json'] = str(return_middle_json).lower()
    if return_model_output is not None:
        form_data['return_model_output'] = str(return_model_output).lower()
    if return_content_list is not None:
        form_data['return_content_list'] = str(return_content_list).lower()
    if return_images is not None:
        form_data['return_images'] = str(return_images).lower()
    if start_page_id is not None:
        form_data['start_page_id'] = str(start_page_id)
    if end_page_id is not None:
        form_data['end_page_id'] = str(end_page_id)
    
    try:
        # 发送POST请求
        response = requests.post(url, files=files, data=form_data)
        
        # 检查响应状态
        response.raise_for_status()
        
        # 返回响应内容
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"PDF解析请求失败: {str(e)}")
    finally:
        # 确保文件被关闭
        files['files'][1].close()

if __name__ == "__main__":
    resp = parse_pdf("/Users/leafw/Documents/workspace/paper-agent/api/llm/tools/test.pdf", output_dir='./', return_md=True, return_middle_json=False, return_model_output=False, return_content_list=True, return_images=False, formula_enable=True, table_enable=True)

    print(resp.get('results').get('test').get('content_list'))
