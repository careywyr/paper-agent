# -*- coding: utf-8 -*-
"""
@file    : pydantic_models.py
@date    : 2025-08-26
@author  : leafw
"""

from pydantic import BaseModel, Field
from typing import Optional, Any

class ResponseVO(BaseModel):
    """统一响应对象"""
    
    # 状态码
    code: int = Field(default=200, description="状态码")
    
    # 消息
    message: str = Field(default="操作成功", description="消息")
    
    # 数据
    data: Optional[Any] = Field(None, description="响应数据")
    
    @classmethod
    def success(cls, data=None):
        """成功响应"""
        return cls(code=200, message="操作成功", data=data)
    
    @classmethod
    def fail(cls, code=500, message="操作失败"):
        """失败响应"""
        return cls(code=code, message=message, data=None)