"""
论文相关的路由
"""
from flask import jsonify, request
from api.routes import main_bp
from api.models.paper import Paper
from api import db
import json

@main_bp.route('/papers', methods=['GET'])
def get_papers():
    """获取论文列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    papers = Paper.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'papers': [paper.to_dict() for paper in papers.items],
        'total': papers.total,
        'pages': papers.pages,
        'current_page': papers.page
    })

@main_bp.route('/papers/<int:paper_id>', methods=['GET'])
def get_paper(paper_id):
    """获取单个论文详情"""
    paper = Paper.query.get_or_404(paper_id)
    return jsonify(paper.to_dict())

@main_bp.route('/papers', methods=['POST'])
def create_paper():
    """创建新论文"""
    data = request.get_json()
    
    if not data or not data.get('arxiv_id') or not data.get('title'):
        return jsonify({'error': '缺少必要的论文信息'}), 400
    
    # 检查论文是否已存在
    existing_paper = Paper.query.filter_by(arxiv_id=data['arxiv_id']).first()
    if existing_paper:
        return jsonify({'error': '该论文已存在', 'paper': existing_paper.to_dict()}), 409
    
    # 创建新论文
    new_paper = Paper(
        arxiv_id=data['arxiv_id'],
        title=data['title'],
        authors=json.dumps(data.get('authors', [])),
        abstract=data.get('abstract', ''),
        pdf_url=data.get('pdf_url'),
        published_date=data.get('published_date'),
        categories=json.dumps(data.get('categories', []))
    )
    
    db.session.add(new_paper)
    db.session.commit()
    
    return jsonify(new_paper.to_dict()), 201

@main_bp.route('/papers/<int:paper_id>', methods=['PUT'])
def update_paper(paper_id):
    """更新论文信息"""
    paper = Paper.query.get_or_404(paper_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供更新数据'}), 400
    
    # 更新论文字段
    if 'title' in data:
        paper.title = data['title']
    if 'authors' in data:
        paper.authors = json.dumps(data['authors'])
    if 'abstract' in data:
        paper.abstract = data['abstract']
    if 'pdf_url' in data:
        paper.pdf_url = data['pdf_url']
    if 'published_date' in data:
        paper.published_date = data['published_date']
    if 'categories' in data:
        paper.categories = json.dumps(data['categories'])
    
    db.session.commit()
    
    return jsonify(paper.to_dict())

@main_bp.route('/papers/<int:paper_id>', methods=['DELETE'])
def delete_paper(paper_id):
    """删除论文"""
    paper = Paper.query.get_or_404(paper_id)
    
    db.session.delete(paper)
    db.session.commit()
    
    return jsonify({'message': '论文已成功删除'})
