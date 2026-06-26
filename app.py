from flask import Flask
from config import BASE_DIR
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.config['WTF_CSRF_ENABLED'] = False
    db.init_app(app)

    from main import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        # 如果没有任何用户，创建一个默认管理员
        from models import User
        if not User.query.first():
            admin = User(username='admin', display_name='管理员', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5100, debug=True)
