"""
论文解析内容模型定义
"""
from datetime import datetime
from sqlalchemy.dialects.postgresql import VECTOR
from api import db

class PaperParsed(db.Model):
    """拆分后的paper内容模型"""
    __tablename__ = 't_paper_parsed'

    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('t_paper.id'), nullable=False, comment='论文id')
    type = db.Column(db.String(16), nullable=True, comment='类型')
    text = db.Column(db.Text, nullable=True, comment='文本')
    page_idx = db.Column(db.Integer, nullable=True, comment='页码')
    img_path = db.Column(db.String(128), nullable=True, comment='如果是照片会有路径')
    image_caption = db.Column(db.Text, nullable=True, comment='图片描述')
    image_footnote = db.Column(db.Text, nullable=True, comment='图片脚注')
    text_format = db.Column(db.String(32), nullable=True, comment='公式类型可能有，应该是latex')
    embeddings = db.Column(VECTOR, nullable=True, comment='向量')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 建立与Paper的关系
    paper = db.relationship('Paper', backref=db.backref('parsed_contents', lazy=True))
    
    def __repr__(self):
        return f'<PaperParsed {self.id}: paper_id={self.paper_id}, type={self.type}>'
    
    def to_dict(self):
        """将模型转换为字典"""
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'type': self.type,
            'text': self.text,
            'page_idx': self.page_idx,
            'img_path': self.img_path,
            'image_caption': self.image_caption,
            'image_footnote': self.image_footnote,
            'text_format': self.text_format,
            'embeddings': self.embeddings,
            'create_time': self.create_time.isoformat()
        }
