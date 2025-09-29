import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from sqlalchemy.exc import IntegrityError
from forms import LoginForm, RegistrationForm
from models import User
from services import UserService
from models import db
from decorators import anonymous_required

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    """ログインページ"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('アカウントが無効化されています。', 'error')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            user.update_last_login()

            try:
                db.session.commit()
                logger.info(f"User {user.username} logged in successfully")
                flash(f'ようこそ、{user.username}さん！', 'success')
            except Exception as e:
                db.session.rollback()
                logger.error(f"Login last_login update error: {e}")
                flash('ログイン処理中にエラーが発生しました。', 'error')
                return render_template('auth/login.html', form=form)

            # リダイレクト先を決定
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            logger.warning(f"Failed login attempt for username: {form.username.data}")
            flash('ユーザー名またはパスワードが正しくありません。', 'error')

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """ログアウト"""
    username = current_user.username
    logout_user()
    logger.info(f"User {username} logged out")
    flash(f'{username}さん、ログアウトしました。', 'info')
    return redirect(url_for('index'))

@auth.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    """ユーザー登録ページ"""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )

        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user registered: {user.username} ({user.email})")
            flash('ユーザー登録が完了しました。ログインしてください。', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            logger.warning(f"Registration failed - duplicate data for username: {form.username.data}, email: {form.email.data}")
            flash('ユーザー名またはメールアドレスが既に使用されています。', 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error for user {form.username.data}: {e}")
            flash('登録中にエラーが発生しました。', 'error')

    return render_template('auth/register.html', form=form)

@auth.route('/profile')
@login_required
def profile():
    """ユーザープロファイルページ"""
    return render_template('auth/profile.html', user=current_user)