"""
论文模型定义
"""
from datetime import datetime
from api import db

class Paper(db.Model):
    """论文模型"""
    __tablename__ = 'papers'

    id = db.Column(db.Integer, primary_key=True)
    arxiv_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    authors = db.Column(db.Text, nullable=False)  # 存储为JSON字符串
    abstract = db.Column(db.Text, nullable=False)
    pdf_url = db.Column(db.String(500), nullable=True)
    published_date = db.Column(db.DateTime, nullable=False)
    categories = db.Column(db.Text, nullable=True)  # 存储为JSON字符串
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Paper {self.arxiv_id}: {self.title}>'
    
    def to_dict(self):
        """将模型转换为字典"""
        return {
            'id': self.id,
            'arxiv_id': self.arxiv_id,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'pdf_url': self.pdf_url,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'categories': self.categories,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
