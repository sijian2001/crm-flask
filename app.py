import logging
from flask import Flask, render_template
from flask_login import LoginManager, login_required
from config import Config
from models import db, User
from auth import auth
from customers import customers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ログ設定初期化
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format=app.config['LOG_FORMAT']
    )

    # データベース初期化
    db.init_app(app)

    # Flask-Login初期化
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'ログインが必要です。'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprintの登録
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(customers, url_prefix='/customers')

    # メインルート
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health')
    @login_required
    def health():
        return {'status': 'healthy', 'user': 'authenticated'}, 200

    # データベースの作成
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=8000)