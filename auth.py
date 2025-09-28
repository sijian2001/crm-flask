from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from forms import LoginForm, RegistrationForm
from models import User, db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """ログインページ"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('アカウントが無効化されています。', 'error')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            user.update_last_login()

            flash(f'ようこそ、{user.username}さん！', 'success')

            # リダイレクト先を決定
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('ユーザー名またはパスワードが正しくありません。', 'error')

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """ログアウト"""
    username = current_user.username
    logout_user()
    flash(f'{username}さん、ログアウトしました。', 'info')
    return redirect(url_for('index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザー登録ページ"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

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
            flash('ユーザー登録が完了しました。ログインしてください。', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('登録中にエラーが発生しました。もう一度お試しください。', 'error')

    return render_template('auth/register.html', form=form)

@auth.route('/profile')
@login_required
def profile():
    """ユーザープロファイルページ"""
    return render_template('auth/profile.html', user=current_user)