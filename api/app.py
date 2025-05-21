"""
Flask应用主入口
"""
from api import create_app, db

app = create_app()

@app.route('/')
def index():
    """API根路由"""
    return {
        'message': 'Paper Agent API 服务正在运行',
        'version': '1.0.0',
        'status': 'online'
    }

@app.cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库已初始化')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
