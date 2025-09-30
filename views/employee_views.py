"""
Employee views module

This module contains all views and API endpoints for employee management
including CRUD operations, organizational management, and HR analytics.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date

from forms import EmployeeForm, EmployeeSearchForm, PositionForm, DepartmentForm
from models import db, Employee, Position, Department, Store
from services import EmployeeService

# Create Blueprint
employees = Blueprint('employees', __name__)


@employees.route('/')
@login_required
def index():
    """従業員一覧ページ"""
    try:
        # フォーム処理
        search_form = EmployeeSearchForm(request.args)

        # ページネーション設定
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # 最大100件

        # 検索・フィルタ条件の取得
        search_params = {}
        if search_form.search.data:
            search_params['search'] = search_form.search.data
        if search_form.store_id.data:
            search_params['store_id'] = search_form.store_id.data
        if search_form.position_id.data:
            search_params['position_id'] = search_form.position_id.data
        if search_form.department_id.data:
            search_params['department_id'] = search_form.department_id.data
        if search_form.employment_status.data:
            search_params['employment_status'] = search_form.employment_status.data
        if search_form.manager_id.data:
            search_params['manager_id'] = search_form.manager_id.data

        # ソート条件
        sort_by = request.args.get('sort_by', 'full_name')
        sort_order = request.args.get('sort_order', 'asc')

        # 従業員取得
        pagination, total_count = EmployeeService.get_employees_with_pagination(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            **search_params
        )

        # 統計情報取得
        statistics = EmployeeService.get_statistics()

        return render_template(
            'employees/index.html',
            title='従業員管理',
            employees=pagination.items,
            pagination=pagination,
            total_count=total_count,
            search_form=search_form,
            statistics=statistics,
            sort_by=sort_by,
            sort_order=sort_order
        )

    except Exception as e:
        flash(f'従業員一覧の取得中にエラーが発生しました: {str(e)}', 'error')
        return render_template('employees/index.html', title='従業員管理', employees=[], statistics={})


@employees.route('/view/<int:employee_id>')
@login_required
def view(employee_id):
    """従業員詳細ページ"""
    try:
        employee = EmployeeService.get_employee_by_id(employee_id)
        if not employee:
            flash('指定された従業員が見つかりません', 'error')
            return redirect(url_for('employees.index'))

        # 部下リスト取得
        subordinates = EmployeeService.get_employees_by_manager(employee.id)

        return render_template(
            'employees/view.html',
            title=f'従業員詳細: {employee.full_name}',
            employee=employee,
            subordinates=subordinates
        )

    except Exception as e:
        flash(f'従業員詳細の取得中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('employees.index'))


@employees.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """従業員登録ページ"""
    form = EmployeeForm()

    if form.validate_on_submit():
        try:
            # フォームデータを辞書に変換
            employee_data = {
                'employee_code': form.employee_code.data,
                'first_name': form.first_name.data,
                'last_name': form.last_name.data,
                'email': form.email.data,
                'phone': form.phone.data,
                'hire_date': form.hire_date.data,
                'employment_status': form.employment_status.data,
                'salary_level': form.salary_level.data,
                'store_id': form.store_id.data,
                'position_id': form.position_id.data,
                'department_id': form.department_id.data,
                'manager_id': form.manager_id.data,
                'emergency_contact_name': form.emergency_contact_name.data,
                'emergency_contact_phone': form.emergency_contact_phone.data,
                'notes': form.notes.data
            }

            success, employee, message = EmployeeService.create_employee(**employee_data)

            if success:
                flash(message, 'success')
                return redirect(url_for('employees.view', employee_id=employee.id))
            else:
                flash(message, 'error')

        except Exception as e:
            flash(f'従業員登録中にエラーが発生しました: {str(e)}', 'error')

    return render_template(
        'employees/create.html',
        title='従業員登録',
        form=form
    )


@employees.route('/edit/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def edit(employee_id):
    """従業員編集ページ"""
    try:
        employee = EmployeeService.get_employee_by_id(employee_id)
        if not employee:
            flash('指定された従業員が見つかりません', 'error')
            return redirect(url_for('employees.index'))

        form = EmployeeForm(employee=employee, obj=employee)

        if form.validate_on_submit():
            try:
                # フォームデータを辞書に変換
                update_data = {
                    'employee_code': form.employee_code.data,
                    'first_name': form.first_name.data,
                    'last_name': form.last_name.data,
                    'email': form.email.data,
                    'phone': form.phone.data,
                    'hire_date': form.hire_date.data,
                    'employment_status': form.employment_status.data,
                    'salary_level': form.salary_level.data,
                    'store_id': form.store_id.data,
                    'position_id': form.position_id.data,
                    'department_id': form.department_id.data,
                    'manager_id': form.manager_id.data,
                    'emergency_contact_name': form.emergency_contact_name.data,
                    'emergency_contact_phone': form.emergency_contact_phone.data,
                    'notes': form.notes.data
                }

                success, updated_employee, message = EmployeeService.update_employee(employee_id, **update_data)

                if success:
                    flash(message, 'success')
                    return redirect(url_for('employees.view', employee_id=employee_id))
                else:
                    flash(message, 'error')

            except Exception as e:
                flash(f'従業員情報更新中にエラーが発生しました: {str(e)}', 'error')

        return render_template(
            'employees/edit.html',
            title=f'従業員編集: {employee.full_name}',
            form=form,
            employee=employee
        )

    except Exception as e:
        flash(f'従業員編集ページの表示中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('employees.index'))


@employees.route('/delete/<int:employee_id>', methods=['POST'])
@login_required
def delete(employee_id):
    """従業員削除（論理削除）"""
    try:
        success, message = EmployeeService.delete_employee(employee_id)

        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')

    except Exception as e:
        flash(f'従業員削除中にエラーが発生しました: {str(e)}', 'error')

    return redirect(url_for('employees.index'))


@employees.route('/<int:employee_id>/transfers', methods=['POST'])
@login_required
def transfer(employee_id):
    """従業員異動処理"""
    try:
        new_store_id = request.form.get('new_store_id', type=int)
        new_position_id = request.form.get('new_position_id', type=int)
        new_department_id = request.form.get('new_department_id', type=int)
        new_manager_id = request.form.get('new_manager_id', type=int)

        if not new_store_id:
            flash('異動先店舗を選択してください', 'error')
            return redirect(url_for('employees.view', employee_id=employee_id))

        success, message = EmployeeService.transfer_employee(
            employee_id, new_store_id, new_position_id, new_department_id, new_manager_id
        )

        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')

    except ValueError as e:
        flash(f'入力値エラー: {str(e)}', 'warning')
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f'Transfer failed for employee {employee_id}: {str(e)}')
        flash('異動処理中にエラーが発生しました', 'error')

    return redirect(url_for('employees.view', employee_id=employee_id))


@employees.route('/<int:employee_id>/promotions', methods=['POST'])
@login_required
def promote(employee_id):
    """従業員昇進処理"""
    try:
        new_position_id = request.form.get('new_position_id', type=int)

        if not new_position_id:
            flash('昇進先役職を選択してください', 'error')
            return redirect(url_for('employees.view', employee_id=employee_id))

        success, message = EmployeeService.promote_employee(employee_id, new_position_id)

        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')

    except ValueError as e:
        flash(f'入力値エラー: {str(e)}', 'warning')
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f'Promotion failed for employee {employee_id}: {str(e)}')
        flash('昇進処理中にエラーが発生しました', 'error')

    return redirect(url_for('employees.view', employee_id=employee_id))


# ===== 組織管理エンドポイント =====

@employees.route('/organizational-chart')
@login_required
def organizational_chart():
    """組織図ページ"""
    try:
        store_id = request.args.get('store_id', type=int)

        # 組織図データ取得
        chart_data = EmployeeService.get_organizational_chart(store_id)

        # 店舗リスト取得
        stores = Store.query.filter_by(status='active').order_by(Store.name).all()

        return render_template(
            'employees/organizational_chart.html',
            title='組織図',
            chart_data=chart_data,
            stores=stores,
            selected_store_id=store_id
        )

    except Exception as e:
        flash(f'組織図の取得中にエラーが発生しました: {str(e)}', 'error')
        return render_template('employees/organizational_chart.html', title='組織図', chart_data=[])


@employees.route('/positions')
@login_required
def positions():
    """役職管理ページ"""
    try:
        positions = EmployeeService.get_positions()

        return render_template(
            'employees/positions.html',
            title='役職管理',
            positions=positions
        )

    except Exception as e:
        flash(f'役職一覧の取得中にエラーが発生しました: {str(e)}', 'error')
        return render_template('employees/positions.html', title='役職管理', positions=[])


@employees.route('/departments')
@login_required
def departments():
    """部署管理ページ"""
    try:
        departments = EmployeeService.get_departments()
        hierarchy = EmployeeService.get_department_hierarchy()

        return render_template(
            'employees/departments.html',
            title='部署管理',
            departments=departments,
            hierarchy=hierarchy
        )

    except Exception as e:
        flash(f'部署一覧の取得中にエラーが発生しました: {str(e)}', 'error')
        return render_template('employees/departments.html', title='部署管理', departments=[], hierarchy=[])


# ===== API エンドポイント =====

@employees.route('/search')
@login_required
def search():
    """従業員AJAX検索"""
    try:
        term = request.args.get('term', '')
        limit = min(request.args.get('limit', 20, type=int), 100)

        employees = EmployeeService.search_employees(term, limit)

        results = []
        for employee in employees:
            results.append({
                'id': employee.id,
                'text': f"{employee.full_name} ({employee.employee_code})",
                'employee_code': employee.employee_code,
                'full_name': employee.full_name,
                'position': employee.position.name if employee.position else None,
                'store': employee.store.name if employee.store else None
            })

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employees.route('/api/statistics')
@login_required
def api_statistics():
    """統計情報API"""
    try:
        statistics = EmployeeService.get_statistics()
        return jsonify(statistics)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employees.route('/api/by-store/<int:store_id>')
@login_required
def api_employees_by_store(store_id):
    """店舗別従業員取得API"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        employees = EmployeeService.get_employees_by_store(store_id, active_only)

        results = []
        for employee in employees:
            results.append({
                'id': employee.id,
                'employee_code': employee.employee_code,
                'full_name': employee.full_name,
                'position': employee.position.name if employee.position else None,
                'department': employee.department.name if employee.department else None,
                'employment_status': employee.employment_status,
                'tenure_years': employee.tenure_years
            })

        return jsonify({'employees': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employees.route('/api/managers/<int:store_id>')
@login_required
def api_managers_for_store(store_id):
    """店舗別管理職取得API"""
    try:
        managers = EmployeeService.get_managers_for_store(store_id)

        results = []
        for manager in managers:
            results.append({
                'id': manager.id,
                'employee_code': manager.employee_code,
                'full_name': manager.full_name,
                'position': manager.position.name if manager.position else None,
                'position_level': manager.position.level if manager.position else 999
            })

        return jsonify({'managers': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employees.route('/api/organizational-chart')
@login_required
def api_organizational_chart():
    """組織図データAPI"""
    try:
        store_id = request.args.get('store_id', type=int)
        chart_data = EmployeeService.get_organizational_chart(store_id)

        return jsonify({'chart_data': chart_data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employees.route('/api/department-hierarchy')
@login_required
def api_department_hierarchy():
    """部署階層データAPI"""
    try:
        hierarchy = EmployeeService.get_department_hierarchy()
        return jsonify({'hierarchy': hierarchy})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== コンテキストプロセッサ =====

@employees.context_processor
def inject_employee_utils():
    """従業員管理用のユーティリティ関数をテンプレートに注入"""
    def format_employment_status(status):
        """雇用状況の日本語表示"""
        status_map = {
            'active': '在職',
            'on_leave': '休職',
            'inactive': '退職',
            'terminated': '解雇'
        }
        return status_map.get(status, status)

    def format_tenure_years(years):
        """勤続年数の表示"""
        if years < 1:
            return f"{int(years * 12)}ヶ月"
        else:
            return f"{years}年"

    def get_status_badge_class(status):
        """雇用状況に応じたCSSクラス"""
        class_map = {
            'active': 'badge-success',
            'on_leave': 'badge-warning',
            'inactive': 'badge-secondary',
            'terminated': 'badge-danger'
        }
        return class_map.get(status, 'badge-secondary')

    def format_salary_range(employee):
        """給与範囲の表示"""
        return employee.salary_range if hasattr(employee, 'salary_range') else "未設定"

    return {
        'format_employment_status': format_employment_status,
        'format_tenure_years': format_tenure_years,
        'get_status_badge_class': get_status_badge_class,
        'format_salary_range': format_salary_range
    }