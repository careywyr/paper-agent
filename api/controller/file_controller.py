# -*- coding: utf-8 -*-
"""
@file    : file_controller.py
@date    : 2025-07-14
@author  : leafw
"""
from flask import Blueprint, request, jsonify

file_controller = Blueprint('file_controller', __name__)

@file_controller.route('/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    file = request.files['file']
    if file:
        return jsonify({'message': '文件上传成功'})
    return jsonify({'message': '文件上传失败'}), 400
