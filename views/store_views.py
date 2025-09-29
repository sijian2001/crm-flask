"""
Store management views

Flask Blueprint for handling store management routes.
Provides CRUD operations, search, filtering, and business status management functionality.
"""
import logging
from typing import Union

from flask import Blueprint, render_template, redirect, url_for, request, abort, current_app, flash, jsonify
from flask_login import login_required, current_user

from forms import StoreForm, StoreSearchForm
from services import StoreService

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('stores')

# Blueprint作成
stores = Blueprint('stores', __name__, template_folder='templates')


@stores.route('/')
@login_required
def index():
    """
    店舗一覧ページ

    検索・フィルタリング・ページネーション機能付きで店舗一覧を表示
    """
    try:
        # 検索フォーム初期化
        search_form = StoreSearchForm()

        # リクエストパラメータ取得
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', '', type=str)
        prefecture = request.args.get('prefecture', '', type=str)
        city = request.args.get('city', '', type=str)
        sort_by = request.args.get('sort_by', 'name', type=str)
        sort_order = request.args.get('sort_order', 'asc', type=str)

        # フォームにデータ設定
        if request.method == 'GET':
            search_form.search.data = search
            search_form.status.data = status
            search_form.prefecture.data = prefecture
            search_form.city.data = city

        # 店舗データ取得
        pagination, total_count = StoreService.get_stores_with_pagination(
            page=page,
            per_page=20,
            search=search if search else None,
            status=status if status else None,
            prefecture=prefecture if prefecture else None,
            city=city if city else None,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # 統計情報取得
        stats = StoreService.get_statistics()

        logger.info(f"Store index accessed by user {current_user.id}, showing {len(pagination.items)} stores")

        return render_template('stores/index.html',
                             pagination=pagination,
                             total_count=total_count,
                             search_form=search_form,
                             stats=stats,
                             current_search=search,
                             current_status=status,
                             current_prefecture=prefecture,
                             current_city=city,
                             sort_by=sort_by,
                             sort_order=sort_order)

    except Exception as e:
        logger.error(f"Error in store index: {str(e)}")
        flash('店舗一覧の取得中にエラーが発生しました。', 'error')
        return render_template('stores/index.html',
                             pagination=None,
                             total_count=0,
                             search_form=StoreSearchForm(),
                             stats={})


@stores.route('/view/<int:store_id>')
@login_required
def view(store_id: int):
    """
    店舗詳細ページ

    指定された店舗の詳細情報を表示
    """
    try:
        store = StoreService.get_store_by_id(store_id)
        if not store:
            flash('指定された店舗が見つかりません。', 'error')
            return redirect(url_for('stores.index'))

        logger.info(f"Store {store_id} viewed by user {current_user.id}")

        return render_template('stores/view.html', store=store)

    except Exception as e:
        logger.error(f"Error viewing store {store_id}: {str(e)}")
        flash('店舗詳細の取得中にエラーが発生しました。', 'error')
        return redirect(url_for('stores.index'))


@stores.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    店舗作成ページ

    新しい店舗を作成
    """
    form = StoreForm()

    if form.validate_on_submit():
        try:
            # 営業時間データを構築
            business_hours = form.get_business_hours()

            success, store, message = StoreService.create_store(
                name=form.name.data,
                address=form.address.data,
                phone=form.phone.data,
                email=form.email.data,
                business_hours=business_hours,
                closed_days=form.closed_days.data,
                status=form.status.data,
                location_prefecture=form.location_prefecture.data,
                location_city=form.location_city.data,
                establishment_date=form.establishment_date.data
            )

            if success:
                flash(message, 'success')
                logger.info(f"Store created: {store.name} by user {current_user.id}")
                return redirect(url_for('stores.view', store_id=store.id))
            else:
                flash(message, 'error')

        except Exception as e:
            logger.error(f"Error creating store: {str(e)}")
            flash('店舗作成中にエラーが発生しました。', 'error')

    return render_template('stores/create.html', form=form)


@stores.route('/edit/<int:store_id>', methods=['GET', 'POST'])
@login_required
def edit(store_id: int):
    """
    店舗編集ページ

    既存店舗の情報を編集
    """
    store = StoreService.get_store_by_id(store_id)
    if not store:
        flash('指定された店舗が見つかりません。', 'error')
        return redirect(url_for('stores.index'))

    form = StoreForm(store=store, obj=store)

    if form.validate_on_submit():
        try:
            # 営業時間データを構築
            business_hours = form.get_business_hours()

            success, updated_store, message = StoreService.update_store(
                store_id=store_id,
                name=form.name.data,
                address=form.address.data,
                phone=form.phone.data,
                email=form.email.data,
                business_hours=business_hours,
                closed_days=form.closed_days.data,
                status=form.status.data,
                location_prefecture=form.location_prefecture.data,
                location_city=form.location_city.data,
                establishment_date=form.establishment_date.data
            )

            if success:
                flash(message, 'success')
                logger.info(f"Store updated: {updated_store.name} by user {current_user.id}")
                return redirect(url_for('stores.view', store_id=store_id))
            else:
                flash(message, 'error')

        except Exception as e:
            logger.error(f"Error updating store {store_id}: {str(e)}")
            flash('店舗更新中にエラーが発生しました。', 'error')

    return render_template('stores/edit.html', form=form, store=store)


@stores.route('/delete/<int:store_id>', methods=['POST'])
@login_required
def delete(store_id: int):
    """
    店舗削除

    指定された店舗を削除
    """
    try:
        store = StoreService.get_store_by_id(store_id)
        if not store:
            flash('指定された店舗が見つかりません。', 'error')
            return redirect(url_for('stores.index'))

        store_name = store.name
        success, message = StoreService.delete_store(store_id)

        if success:
            flash(message, 'success')
            logger.info(f"Store deleted: {store_name} by user {current_user.id}")
        else:
            flash(message, 'error')

    except Exception as e:
        logger.error(f"Error deleting store {store_id}: {str(e)}")
        flash('店舗削除中にエラーが発生しました。', 'error')

    return redirect(url_for('stores.index'))


@stores.route('/search')
@login_required
def search():
    """
    店舗検索API

    AJAX用の検索エンドポイント
    """
    try:
        search_term = request.args.get('q', '', type=str)
        status = request.args.get('status', '', type=str)
        prefecture = request.args.get('prefecture', '', type=str)
        city = request.args.get('city', '', type=str)

        # 検索実行
        pagination, total_count = StoreService.get_stores_with_pagination(
            page=1,
            per_page=50,  # API では多めに返す
            search=search_term if search_term else None,
            status=status if status else None,
            prefecture=prefecture if prefecture else None,
            city=city if city else None
        )

        # JSON形式で結果を返す
        stores_data = []
        for store in pagination.items:
            stores_data.append({
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'status': store.status,
                'location_full': store.location_full,
                'business_years': store.business_years,
                'is_active': store.is_active
            })

        return jsonify({
            'stores': stores_data,
            'total_count': total_count
        })

    except Exception as e:
        logger.error(f"Error in store search API: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500


@stores.route('/api/cities/<prefecture>')
@login_required
def get_cities(prefecture: str):
    """
    指定都道府県の市区町村一覧API

    Args:
        prefecture: 都道府県名

    Returns:
        JSON形式の市区町村リスト
    """
    try:
        cities = StoreService.get_cities_by_prefecture(prefecture)
        return jsonify({'cities': cities})

    except Exception as e:
        logger.error(f"Error getting cities for {prefecture}: {str(e)}")
        return jsonify({'error': 'Failed to get cities'}), 500


@stores.route('/api/statistics')
@login_required
def get_statistics():
    """
    店舗統計情報API

    Returns:
        JSON形式の統計情報
    """
    try:
        stats = StoreService.get_statistics()
        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting store statistics: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500


@stores.route('/api/prefectures')
@login_required
def get_prefectures():
    """
    都道府県一覧API

    Returns:
        JSON形式の都道府県リスト
    """
    try:
        prefectures = StoreService.get_prefectures()
        return jsonify({'prefectures': prefectures})

    except Exception as e:
        logger.error(f"Error getting prefectures: {str(e)}")
        return jsonify({'error': 'Failed to get prefectures'}), 500


# エラーハンドラー
@stores.errorhandler(404)
def store_not_found(error):
    """店舗が見つからない場合のエラーハンドラー"""
    flash('指定された店舗が見つかりません。', 'error')
    return redirect(url_for('stores.index'))


@stores.errorhandler(500)
def store_server_error(error):
    """サーバーエラーのハンドラー"""
    logger.error(f"Store server error: {str(error)}")
    flash('サーバーエラーが発生しました。', 'error')
    return redirect(url_for('stores.index'))


# コンテキストプロセッサ
@stores.context_processor
def inject_store_utilities():
    """テンプレート用のユーティリティ関数を注入"""
    def format_business_hours(hours):
        """営業時間の表示用フォーマット"""
        if not hours:
            return {}

        days_jp = {
            'mon': '月',
            'tue': '火',
            'wed': '水',
            'thu': '木',
            'fri': '金',
            'sat': '土',
            'sun': '日'
        }

        formatted = {}
        for day, time in hours.items():
            if day in days_jp:
                formatted[days_jp[day]] = time if time != 'closed' else '休業'

        return formatted

    def get_status_badge_class(status):
        """ステータスに応じたCSSクラスを返す"""
        status_classes = {
            'active': 'badge-success',
            'temporarily_closed': 'badge-warning',
            'inactive': 'badge-secondary'
        }
        return status_classes.get(status, 'badge-secondary')

    def get_status_text(status):
        """ステータスの表示用テキストを返す"""
        status_texts = {
            'active': '営業中',
            'temporarily_closed': '一時休業',
            'inactive': '休業'
        }
        return status_texts.get(status, status)

    return {
        'format_business_hours': format_business_hours,
        'get_status_badge_class': get_status_badge_class,
        'get_status_text': get_status_text
    }