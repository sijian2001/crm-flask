from typing import Union
from flask import Blueprint, render_template, redirect, url_for, request, abort, current_app
from flask_login import login_required, current_user
from forms import CustomerForm, CustomerSearchForm
from services import CustomerService
from customer_config import CustomerConfig
from utils.error_handlers import (
    handle_customer_operation_success,
    handle_customer_operation_error,
    log_customer_access
)
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
    items_per_page = CustomerConfig.get_items_per_page(current_app.config)

    # 検索フォーム
    search_form = CustomerSearchForm()
    if search:
        search_form.search.data = search

    # サービス層を使用してデータを取得
    customer_pagination = CustomerService.get_customers_with_pagination(
        page=page,
        per_page=items_per_page,
        search=search
    )

    logger.info(f'Customer list accessed by user {current_user.username}, page {page}, search: "{search}"')

    return render_template(
        'customers/index.html',
        customers=customer_pagination,
        search_form=search_form,
        search=search
    )

@customers.route('/create', methods=['GET', 'POST'])
@login_required
def create() -> Union[str, 'Response']:
    """顧客新規作成ページ"""
    form = CustomerForm()

    if form.validate_on_submit():
        success, customer, error_message = CustomerService.create_customer(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            company=form.company.data,
            address=form.address.data,
            notes=form.notes.data
        )

        if success:
            handle_customer_operation_success('created', customer.full_name)
            return redirect(url_for('customers.view', id=customer.id))
        else:
            handle_customer_operation_error('creation', error_message)

    return render_template('customers/form.html', form=form, title='顧客新規登録')

@customers.route('/<int:id>')
@login_required
def view(id: int) -> Union[str, 'Response']:
    """顧客詳細ページ"""
    customer = CustomerService.get_customer_by_id(id)
    if not customer:
        abort(404)

    can_access, warning_message = CustomerService.validate_customer_access(customer)
    if warning_message:
        flash(warning_message, 'warning')

    log_customer_access(customer.full_name, 'viewed')
    return render_template('customers/view.html', customer=customer)

@customers.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id: int) -> Union[str, 'Response']:
    """顧客編集ページ"""
    customer = CustomerService.get_customer_by_id(id)
    if not customer:
        abort(404)

    form = CustomerForm(customer=customer, obj=customer)

    if form.validate_on_submit():
        success, error_message = CustomerService.update_customer(
            customer=customer,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            company=form.company.data,
            address=form.address.data,
            notes=form.notes.data
        )

        if success:
            handle_customer_operation_success('updated', customer.full_name)
            return redirect(url_for('customers.view', id=customer.id))
        else:
            handle_customer_operation_error('update', error_message, customer.full_name)

    return render_template('customers/form.html', form=form, customer=customer, title='顧客情報編集')

@customers.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id: int) -> 'Response':
    """顧客削除（無効化）"""
    customer = CustomerService.get_customer_by_id(id)
    if not customer:
        abort(404)

    success, error_message = CustomerService.deactivate_customer(customer)

    if success:
        handle_customer_operation_success('deactivated', customer.full_name)
        return redirect(url_for('customers.index'))
    else:
        handle_customer_operation_error('deactivation', error_message, customer.full_name)
        return redirect(url_for('customers.view', id=customer.id))

@customers.route('/<int:id>/activate', methods=['POST'])
@login_required
def activate(id: int) -> 'Response':
    """顧客有効化"""
    customer = CustomerService.get_customer_by_id(id)
    if not customer:
        abort(404)

    success, error_message = CustomerService.activate_customer(customer)

    if success:
        handle_customer_operation_success('activated', customer.full_name)
        return redirect(url_for('customers.view', id=customer.id))
    else:
        handle_customer_operation_error('activation', error_message, customer.full_name)
        return redirect(url_for('customers.view', id=customer.id))

@customers.route('/search')
@login_required
def search() -> 'Response':
    """顧客検索（AJAX対応）"""
    search_query = request.args.get('q', '', type=str)

    if not search_query:
        return redirect(url_for('customers.index'))

    return redirect(url_for('customers.index', search=search_query))