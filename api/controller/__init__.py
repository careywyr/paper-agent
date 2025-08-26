"""
路由包初始化文件
"""
from flask import Blueprint

# 创建主蓝图
main_bp = Blueprint('main', __name__, url_prefix='/api')

# 导入路由
from api.controller import paper_controller, file_controller
