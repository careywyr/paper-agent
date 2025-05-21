"""
论文服务层 - 处理与论文相关的业务逻辑
"""
import json
from datetime import datetime
from api.models.paper import Paper
from api import db

class PaperService:
    """论文服务类"""
    
    @staticmethod
    def get_all_papers(page=1, per_page=10):
        """
        获取所有论文，支持分页
        
        Args:
            page: 页码
            per_page: 每页数量
            
        Returns:
            分页后的论文列表和分页信息
        """
        papers = Paper.query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'papers': [paper.to_dict() for paper in papers.items],
            'total': papers.total,
            'pages': papers.pages,
            'current_page': papers.page
        }
    
    @staticmethod
    def get_paper_by_id(paper_id):
        """
        通过ID获取论文
        
        Args:
            paper_id: 论文ID
            
        Returns:
            论文对象或None
        """
        return Paper.query.get(paper_id)
    
    @staticmethod
    def get_paper_by_arxiv_id(arxiv_id):
        """
        通过arXiv ID获取论文
        
        Args:
            arxiv_id: arXiv ID
            
        Returns:
            论文对象或None
        """
        return Paper.query.filter_by(arxiv_id=arxiv_id).first()
    
    @staticmethod
    def create_paper(paper_data):
        """
        创建新论文
        
        Args:
            paper_data: 论文数据字典
            
        Returns:
            新创建的论文对象
        """
        # 检查必要字段
        if not paper_data.get('arxiv_id') or not paper_data.get('title'):
            raise ValueError("论文必须包含arxiv_id和title字段")
        
        # 检查论文是否已存在
        existing_paper = PaperService.get_paper_by_arxiv_id(paper_data['arxiv_id'])
        if existing_paper:
            return existing_paper
        
        # 处理日期字段
        published_date = paper_data.get('published_date')
        if isinstance(published_date, str):
            try:
                published_date = datetime.fromisoformat(published_date)
            except ValueError:
                published_date = datetime.utcnow()
        
        # 创建新论文
        new_paper = Paper(
            arxiv_id=paper_data['arxiv_id'],
            title=paper_data['title'],
            authors=json.dumps(paper_data.get('authors', [])),
            abstract=paper_data.get('abstract', ''),
            pdf_url=paper_data.get('pdf_url'),
            published_date=published_date or datetime.utcnow(),
            categories=json.dumps(paper_data.get('categories', []))
        )
        
        db.session.add(new_paper)
        db.session.commit()
        
        return new_paper
    
    @staticmethod
    def update_paper(paper_id, paper_data):
        """
        更新论文信息
        
        Args:
            paper_id: 论文ID
            paper_data: 更新的论文数据
            
        Returns:
            更新后的论文对象或None（如果论文不存在）
        """
        paper = PaperService.get_paper_by_id(paper_id)
        if not paper:
            return None
        
        # 更新论文字段
        if 'title' in paper_data:
            paper.title = paper_data['title']
        if 'authors' in paper_data:
            paper.authors = json.dumps(paper_data['authors'])
        if 'abstract' in paper_data:
            paper.abstract = paper_data['abstract']
        if 'pdf_url' in paper_data:
            paper.pdf_url = paper_data['pdf_url']
        if 'published_date' in paper_data:
            published_date = paper_data['published_date']
            if isinstance(published_date, str):
                try:
                    published_date = datetime.fromisoformat(published_date)
                    paper.published_date = published_date
                except ValueError:
                    pass
        if 'categories' in paper_data:
            paper.categories = json.dumps(paper_data['categories'])
        
        db.session.commit()
        
        return paper
    
    @staticmethod
    def delete_paper(paper_id):
        """
        删除论文
        
        Args:
            paper_id: 论文ID
            
        Returns:
            bool: 是否成功删除
        """
        paper = PaperService.get_paper_by_id(paper_id)
        if not paper:
            return False
        
        db.session.delete(paper)
        db.session.commit()
        
        return True
    
    @staticmethod
    def search_papers(query, page=1, per_page=10):
        """
        搜索论文
        
        Args:
            query: 搜索关键词
            page: 页码
            per_page: 每页数量
            
        Returns:
            匹配的论文列表和分页信息
        """
        search = f"%{query}%"
        papers = Paper.query.filter(
            (Paper.title.ilike(search)) | 
            (Paper.abstract.ilike(search)) | 
            (Paper.authors.ilike(search))
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'papers': [paper.to_dict() for paper in papers.items],
            'total': papers.total,
            'pages': papers.pages,
            'current_page': papers.page
        }
