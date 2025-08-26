# -*- coding: utf-8 -*-
"""
@file    : home_controller.py
@date    : 2025-08-26
@author  : leafw
"""

from flask import jsonify
from api.decorator.request_param import request_param
from flask import Blueprint


home_bp = Blueprint('home', __name__, url_prefix='/pa/home')

@home_bp.route('/search', methods=['GET'])
@request_param(query=str)
def search(query:str):
    return jsonify({"message": query})


@home_bp.route('/chat', methods=['GET'])
@request_param(query=str, conversation_id=str)
def chat(query:str, conversation_id:str=None):
    return jsonify({"message": query})
