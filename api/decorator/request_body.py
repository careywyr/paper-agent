# -*- coding: utf-8 -*-
"""
@file    : request_body.py
@date    : 2025-08-26
@author  : leafw
"""


from functools import wraps
from flask import request
from pydantic import ValidationError
from models.pydantic_models import ResponseVO


def request_body(model_class):
    """
    请求体解析装饰器
    
    Args:
        model_class: Pydantic模型类
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 解析请求体并创建模型对象
                obj = model_class(**request.get_json(force=True) or {})
                # 将模型对象作为第一个参数传递给被装饰的函数
                return func(obj, *args, **kwargs)
            except ValidationError as e:
                # 处理参数验证错误
                response = ResponseVO.fail(400, f'参数验证失败: {str(e)}')
                return response.model_dump(), 400
        return wrapper
    return decorator