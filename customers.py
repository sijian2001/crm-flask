from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from forms import CustomerForm, CustomerSearchForm
from models import Customer, db
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('customers')

customers = Blueprint('customers', __name__)

@customers.route('/')
@login_required
def index():
    """顧客一覧ページ"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    per_page = 10  # 1ページあたりの表示件数

    # 検索フォーム
    search_form = CustomerSearchForm()
    if search:
        search_form.search.data = search

    # クエリの構築
    query = Customer.query.filter_by(is_active=True)

    if search:
        # 名前、メール、会社名での検索
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Customer.first_name.ilike(search_term),
                Customer.last_name.ilike(search_term),
                Customer.email.ilike(search_term),
                Customer.company.ilike(search_term)
            )
        )

    # ページネーション
    customers_paginated = query.order_by(Customer.updated_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    logger.info(f'Customer list accessed by user {current_user.username}, page {page}, search: "{search}"')

    return render_template(
        'customers/index.html',
        customers=customers_paginated,
        search_form=search_form,
        search=search
    )

@customers.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """顧客新規作成ページ"""
    form = CustomerForm()

    if form.validate_on_submit():
        try:
            customer = Customer(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                company=form.company.data,
                address=form.address.data,
                notes=form.notes.data
            )

            db.session.add(customer)
            db.session.commit()

            logger.info(f'New customer created: {customer.full_name} by user {current_user.username}')
            flash(f'顧客「{customer.full_name}」を登録しました。', 'success')
            return redirect(url_for('customers.view', id=customer.id))

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f'Customer creation failed: {str(e)} by user {current_user.username}')
            flash('顧客登録中にエラーが発生しました。メールアドレスが重複している可能性があります。', 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Unexpected error during customer creation: {str(e)} by user {current_user.username}')
            flash('顧客登録中に予期しないエラーが発生しました。', 'error')

    return render_template('customers/form.html', form=form, title='顧客新規登録')

@customers.route('/<int:id>')
@login_required
def view(id):
    """顧客詳細ページ"""
    customer = Customer.query.get_or_404(id)

    if not customer.is_active:
        flash('指定された顧客は無効化されています。', 'warning')

    logger.info(f'Customer {customer.full_name} viewed by user {current_user.username}')
    return render_template('customers/view.html', customer=customer)

@customers.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """顧客編集ページ"""
    customer = Customer.query.get_or_404(id)

    if not customer.is_active:
        flash('無効化された顧客は編集できません。', 'error')
        return redirect(url_for('customers.view', id=customer.id))

    form = CustomerForm(customer=customer, obj=customer)

    if form.validate_on_submit():
        try:
            customer.update_info(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                company=form.company.data,
                address=form.address.data,
                notes=form.notes.data
            )

            db.session.commit()

            logger.info(f'Customer {customer.full_name} updated by user {current_user.username}')
            flash(f'顧客「{customer.full_name}」の情報を更新しました。', 'success')
            return redirect(url_for('customers.view', id=customer.id))

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f'Customer update failed: {str(e)} by user {current_user.username}')
            flash('顧客情報更新中にエラーが発生しました。メールアドレスが重複している可能性があります。', 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Unexpected error during customer update: {str(e)} by user {current_user.username}')
            flash('顧客情報更新中に予期しないエラーが発生しました。', 'error')

    return render_template('customers/form.html', form=form, customer=customer, title='顧客情報編集')

@customers.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """顧客削除（無効化）"""
    customer = Customer.query.get_or_404(id)

    if not customer.is_active:
        flash('指定された顧客は既に無効化されています。', 'warning')
        return redirect(url_for('customers.view', id=customer.id))

    try:
        customer.deactivate()
        db.session.commit()

        logger.info(f'Customer {customer.full_name} deactivated by user {current_user.username}')
        flash(f'顧客「{customer.full_name}」を無効化しました。', 'info')
        return redirect(url_for('customers.index'))

    except Exception as e:
        db.session.rollback()
        logger.error(f'Customer deactivation failed: {str(e)} by user {current_user.username}')
        flash('顧客無効化中にエラーが発生しました。', 'error')
        return redirect(url_for('customers.view', id=customer.id))

@customers.route('/<int:id>/activate', methods=['POST'])
@login_required
def activate(id):
    """顧客有効化"""
    customer = Customer.query.get_or_404(id)

    if customer.is_active:
        flash('指定された顧客は既に有効化されています。', 'info')
        return redirect(url_for('customers.view', id=customer.id))

    try:
        customer.activate()
        db.session.commit()

        logger.info(f'Customer {customer.full_name} activated by user {current_user.username}')
        flash(f'顧客「{customer.full_name}」を有効化しました。', 'success')
        return redirect(url_for('customers.view', id=customer.id))

    except Exception as e:
        db.session.rollback()
        logger.error(f'Customer activation failed: {str(e)} by user {current_user.username}')
        flash('顧客有効化中にエラーが発生しました。', 'error')
        return redirect(url_for('customers.view', id=customer.id))

@customers.route('/search')
@login_required
def search():
    """顧客検索（AJAX対応）"""
    search_term = request.args.get('q', '', type=str)

    if not search_term:
        return redirect(url_for('customers.index'))

    return redirect(url_for('customers.index', search=search_term))