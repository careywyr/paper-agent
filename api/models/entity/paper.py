"""
论文模型定义
"""
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from api import db

class Paper(db.Model):
    """论文模型"""
    __tablename__ = 't_paper'

    id = db.Column(db.Integer, primary_key=True)
    arxiv_id = db.Column(db.String(16), unique=True, nullable=True, index=True)
    file_path = db.Column(db.String(128), nullable=True, comment='文件路径')
    title = db.Column(db.String(255), nullable=True, comment='文章标题')
    authors = db.Column(ARRAY(db.String), nullable=True, comment='作者')
    abstract = db.Column(db.Text, nullable=True, comment='摘要')
    source_url = db.Column(db.String(128), nullable=True, comment='文章原地址')
    published_date = db.Column(db.Date, nullable=True, comment='发布日期')
    categories = db.Column(ARRAY(db.String), nullable=True, comment='分类')
    tags = db.Column(ARRAY(db.String), nullable=True, comment='标签')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Paper {self.arxiv_id}: {self.title}>'
    
    def to_dict(self):
        """将模型转换为字典"""
        return {
            'id': self.id,
            'arxiv_id': self.arxiv_id,
            'file_path': self.file_path,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'source_url': self.source_url,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'categories': self.categories,
            'tags': self.tags,
            'create_time': self.create_time.isoformat(),
            'update_time': self.update_time.isoformat()
        }
