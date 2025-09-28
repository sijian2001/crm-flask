"""
Product management views

Flask Blueprint for handling product and category management routes.
Provides CRUD operations, search, filtering, and stock management functionality.
"""
from typing import Union
from flask import Blueprint, render_template, redirect, url_for, request, abort, current_app, flash
from flask_login import login_required, current_user
from forms import (
    ProductForm, ProductSearchForm, CategoryForm, CategorySearchForm, StockUpdateForm
)
from services import ProductService, CategoryService
from product_config import ProductConfig
from utils.error_handlers import (
    handle_customer_operation_success,
    handle_customer_operation_error,
    log_customer_access,
    CustomerOperationResult,
    validate_product_operation,
    validate_category_operation
)
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('products')

products = Blueprint('products', __name__)


@products.route('/')
@login_required
def index():
    """製品一覧ページ"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category_id = request.args.get('category_id', 0, type=int)
    low_stock_only = request.args.get('low_stock_only', False, type=bool)
    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)
    items_per_page = ProductConfig.get_default_per_page()

    # 検索フォーム
    search_form = ProductSearchForm()
    if search:
        search_form.search.data = search
    if category_id:
        search_form.category_id.data = category_id
    if low_stock_only:
        search_form.low_stock_only.data = low_stock_only

    # サービス層を使用してデータを取得
    product_pagination = ProductService.get_products_with_pagination(
        page=page,
        per_page=items_per_page,
        search=search,
        category_id=category_id if category_id > 0 else None,
        low_stock_only=low_stock_only,
        sort_by=sort_by,
        sort_order=sort_order
    )

    logger.info(f'Product list accessed by user {current_user.username}, page {page}, search: "{search}"')

    return render_template(
        'products/index.html',
        products=product_pagination,
        search_form=search_form,
        search=search,
        category_id=category_id,
        low_stock_only=low_stock_only,
        sort_by=sort_by,
        sort_order=sort_order
    )


@products.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """製品作成ページ"""
    form = ProductForm()

    if form.validate_on_submit():
        # サービス層を使用して製品を作成
        success, product, error = ProductService.create_product(
            name=form.name.data.strip(),
            sku=form.sku.data.strip(),
            price=float(form.price.data),
            category_id=form.category_id.data,
            description=form.description.data.strip() if form.description.data else None,
            cost=float(form.cost.data) if form.cost.data else None,
            stock_quantity=form.stock_quantity.data,
            min_stock_level=form.min_stock_level.data
        )

        if success:
            handle_customer_operation_success('created', product.name, f'製品「{product.name}」を登録しました。')
            logger.info(f'Product {product.name} ({product.sku}) created by user {current_user.username}')
            return redirect(url_for('products.view', id=product.id))
        else:
            handle_customer_operation_error('creation', error)

    return render_template('products/create.html', form=form)


@products.route('/<int:id>')
@login_required
def view(id: int):
    """製品詳細ページ"""
    product = ProductService.get_product_by_id(id)
    if not product:
        abort(404)

    # アクセスをログに記録
    log_customer_access(product.name, 'viewed')

    return render_template('products/view.html', product=product)


@products.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id: int):
    """製品編集ページ"""
    product = ProductService.get_product_by_id(id)
    if not product:
        abort(404)

    # 製品の操作権限チェック
    is_valid, error_message = validate_product_operation(product, 'edit')
    if not is_valid:
        handle_customer_operation_error('update', error_message, product.name)
        return redirect(url_for('products.view', id=id))

    form = ProductForm(product=product, obj=product)

    # フォームのparent_idフィールドを設定（カテゴリ編集用）
    if hasattr(form, 'parent_id'):
        form.parent_id.data = product.category.parent_id if product.category.parent_id else 0

    if form.validate_on_submit():
        # サービス層を使用して製品を更新
        success, error = ProductService.update_product(
            product=product,
            name=form.name.data.strip(),
            sku=form.sku.data.strip(),
            price=float(form.price.data),
            category_id=form.category_id.data,
            description=form.description.data.strip() if form.description.data else None,
            cost=float(form.cost.data) if form.cost.data else None,
            stock_quantity=form.stock_quantity.data,
            min_stock_level=form.min_stock_level.data
        )

        if success:
            handle_customer_operation_success('updated', product.name, f'製品「{product.name}」の情報を更新しました。')
            logger.info(f'Product {product.name} ({product.sku}) updated by user {current_user.username}')
            return redirect(url_for('products.view', id=product.id))
        else:
            handle_customer_operation_error('update', error, product.name)

    return render_template('products/edit.html', form=form, product=product)


@products.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id: int):
    """製品削除（無効化）"""
    product = ProductService.get_product_by_id(id)
    if not product:
        abort(404)

    # 製品の操作権限チェック
    is_valid, error_message = validate_product_operation(product, 'delete')
    if not is_valid:
        handle_customer_operation_error('deletion', error_message, product.name)
        return redirect(url_for('products.view', id=id))

    # サービス層を使用して製品を無効化
    success, error = ProductService.deactivate_product(product)

    if success:
        handle_customer_operation_success('deactivated', product.name, f'製品「{product.name}」を無効化しました。')
        logger.info(f'Product {product.name} ({product.sku}) deactivated by user {current_user.username}')
        return redirect(url_for('products.index'))
    else:
        handle_customer_operation_error('deletion', error, product.name)
        return redirect(url_for('products.view', id=id))


@products.route('/<int:id>/activate', methods=['POST'])
@login_required
def activate(id: int):
    """製品有効化"""
    product = ProductService.get_product_by_id(id)
    if not product:
        abort(404)

    # サービス層を使用して製品を有効化
    success, error = ProductService.activate_product(product)

    if success:
        handle_customer_operation_success('activated', product.name, f'製品「{product.name}」を有効化しました。')
        logger.info(f'Product {product.name} ({product.sku}) activated by user {current_user.username}')
    else:
        handle_customer_operation_error('activation', error, product.name)

    return redirect(url_for('products.view', id=id))


@products.route('/<int:id>/update_stock', methods=['GET', 'POST'])
@login_required
def update_stock(id: int):
    """在庫更新ページ"""
    product = ProductService.get_product_by_id(id)
    if not product:
        abort(404)

    # 製品の操作権限チェック
    is_valid, error_message = validate_product_operation(product, 'stock_update')
    if not is_valid:
        handle_customer_operation_error('update', error_message, product.name)
        return redirect(url_for('products.view', id=id))

    form = StockUpdateForm()
    form.stock_quantity.data = product.stock_quantity

    if form.validate_on_submit():
        # サービス層を使用して在庫を更新
        success, error = ProductService.update_stock(product, form.stock_quantity.data)

        if success:
            handle_customer_operation_success('updated', product.name, f'製品「{product.name}」の在庫を更新しました。')
            logger.info(f'Product {product.name} stock updated to {form.stock_quantity.data} by user {current_user.username}')
            return redirect(url_for('products.view', id=id))
        else:
            handle_customer_operation_error('update', error, product.name)

    return render_template('products/update_stock.html', form=form, product=product)


# カテゴリ管理ルート
@products.route('/categories/')
@login_required
def categories_index():
    """カテゴリ一覧ページ"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    parent_id = request.args.get('parent_id', 0, type=int)
    items_per_page = ProductConfig.get_default_per_page()

    # 検索フォーム
    search_form = CategorySearchForm()
    if search:
        search_form.search.data = search
    if parent_id != 0:
        search_form.parent_id.data = parent_id

    # サービス層を使用してデータを取得
    if parent_id == -1:  # ルートカテゴリのみ
        parent_filter = None
    elif parent_id > 0:
        parent_filter = parent_id
    else:
        parent_filter = None

    category_pagination = CategoryService.get_categories_with_pagination(
        page=page,
        per_page=items_per_page,
        search=search,
        parent_id=parent_filter
    )

    # N+1問題を防ぐため、表示されるカテゴリの製品数を一括取得
    category_ids = [category.id for category in category_pagination.items]
    if category_ids:
        categories_with_counts = CategoryService.get_categories_with_product_counts(category_ids)
        # カテゴリIDをキーとした製品数のマップを作成
        product_count_map = {category.id: count for category, count in categories_with_counts}
    else:
        product_count_map = {}

    logger.info(f'Category list accessed by user {current_user.username}, page {page}, search: "{search}"')

    return render_template(
        'products/categories/index.html',
        categories=category_pagination,
        search_form=search_form,
        search=search,
        parent_id=parent_id,
        product_count_map=product_count_map
    )


@products.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """カテゴリ作成ページ"""
    form = CategoryForm()

    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data != 0 else None

        # サービス層を使用してカテゴリを作成
        success, category, error = CategoryService.create_category(
            name=form.name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            parent_id=parent_id
        )

        if success:
            handle_customer_operation_success('created', category.name, f'カテゴリ「{category.name}」を登録しました。')
            logger.info(f'Category {category.name} created by user {current_user.username}')
            return redirect(url_for('products.view_category', id=category.id))
        else:
            handle_customer_operation_error('creation', error)

    return render_template('products/categories/create.html', form=form)


@products.route('/categories/<int:id>')
@login_required
def view_category(id: int):
    """カテゴリ詳細ページ（N+1問題対策済み）"""
    category = CategoryService.get_category_by_id(id)
    if not category:
        abort(404)

    # アクセスをログに記録
    log_customer_access(category.name, 'viewed')

    # このカテゴリの製品を取得
    products_pagination = ProductService.get_products_with_pagination(
        page=1,
        per_page=10,
        category_id=id
    )

    # 子カテゴリの製品数を一括取得（N+1問題対策）
    child_category_ids = [child.id for child in category.children if child.is_active]
    if child_category_ids:
        children_with_counts = CategoryService.get_categories_with_product_counts(child_category_ids)
        child_product_count_map = {category.id: count for category, count in children_with_counts}
    else:
        child_product_count_map = {}

    return render_template(
        'products/categories/view.html',
        category=category,
        products=products_pagination,
        child_product_count_map=child_product_count_map
    )


@products.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id: int):
    """カテゴリ編集ページ"""
    category = CategoryService.get_category_by_id(id)
    if not category:
        abort(404)

    # カテゴリの操作権限チェック
    is_valid, error_message = validate_category_operation(category, 'edit')
    if not is_valid:
        handle_customer_operation_error('update', error_message, category.name)
        return redirect(url_for('products.view_category', id=id))

    form = CategoryForm(category=category, obj=category)

    # フォームのparent_idフィールドを設定
    form.parent_id.data = category.parent_id if category.parent_id else 0

    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data != 0 else None

        # サービス層を使用してカテゴリを更新
        success, error = CategoryService.update_category(
            category=category,
            name=form.name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            parent_id=parent_id
        )

        if success:
            handle_customer_operation_success('updated', category.name, f'カテゴリ「{category.name}」の情報を更新しました。')
            logger.info(f'Category {category.name} updated by user {current_user.username}')
            return redirect(url_for('products.view_category', id=category.id))
        else:
            handle_customer_operation_error('update', error, category.name)

    return render_template('products/categories/edit.html', form=form, category=category)


@products.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id: int):
    """カテゴリ削除（無効化）"""
    category = CategoryService.get_category_by_id(id)
    if not category:
        abort(404)

    # カテゴリの操作権限チェック
    is_valid, error_message = validate_category_operation(category, 'delete')
    if not is_valid:
        handle_customer_operation_error('deletion', error_message, category.name)
        return redirect(url_for('products.view_category', id=id))

    # サービス層を使用してカテゴリを無効化
    success, error = CategoryService.deactivate_category(category)

    if success:
        handle_customer_operation_success('deactivated', category.name, f'カテゴリ「{category.name}」を無効化しました。')
        logger.info(f'Category {category.name} deactivated by user {current_user.username}')
        return redirect(url_for('products.categories_index'))
    else:
        handle_customer_operation_error('deletion', error, category.name)
        return redirect(url_for('products.view_category', id=id))