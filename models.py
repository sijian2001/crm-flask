from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_active = True
        self.created_at = datetime.utcnow()

    def set_password(self, password):
        """パスワードをハッシュ化して保存"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """パスワードを検証"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """最終ログイン時刻を更新"""
        self.last_login = datetime.utcnow()

    def get_id(self):
        """Flask-Loginで必要なユーザーID取得メソッド"""
        return str(self.id)

    def is_authenticated(self):
        """認証済みかどうか"""
        return True

    def is_anonymous(self):
        """匿名ユーザーかどうか"""
        return False

    def __repr__(self):
        return f'<User {self.username}>'