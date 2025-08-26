# -*- coding: utf-8 -*-
"""
@file    : request_param.py
@date    : 2025-08-26
@author  : leafw
"""

from functools import wraps
from flask import request


def request_param(**param_types):
    """
    请求参数装饰器，用于处理GET请求的URL参数
    
    用法示例:
    @request_param(id=int, name=str, active=bool)
    def my_route(id, name, active=False):
        # 函数体
    
    参数:
        **param_types: 参数名和类型的键值对
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for param_name, param_type in param_types.items():
                # 检查是否是必需参数（在函数定义中没有默认值）
                is_required = param_name in func.__code__.co_varnames[:func.__code__.co_argcount] and \
                             param_name not in kwargs and \
                             func.__defaults__ is None or \
                             param_name not in func.__code__.co_varnames[func.__code__.co_argcount - len(func.__defaults__ or ()):] if func.__defaults__ else True
                
                # 获取请求参数
                value = request.args.get(param_name)
                
                # 如果是必需参数但值为None
                if is_required and value is None:
                    # TODO
                    pass
                
                # 如果有值，进行类型转换
                if value is not None:
                    try:
                        if param_type is bool:
                            # 特殊处理布尔类型
                            value = value.lower() in ('true', 'yes', '1', 'y')
                        else:
                            value = param_type(value)
                        kwargs[param_name] = value
                    except ValueError:
                        # TODO
                        pass
            
            return func(*args, **kwargs)
        return wrapper
    return decorator