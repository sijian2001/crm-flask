from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user

def admin_required(f):
    """管理者権限が必要なページ用デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('ログインが必要です。', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        # 将来的に管理者フラグを追加する場合
        # if not current_user.is_admin:
        #     flash('管理者権限が必要です。', 'error')
        #     return redirect(url_for('index'))

        return f(*args, **kwargs)
    return decorated_function

def anonymous_required(f):
    """匿名ユーザー（未ログイン）のみアクセス可能なページ用デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function