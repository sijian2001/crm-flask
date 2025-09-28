import pytest
from models import Customer, db

class TestCustomerViews:
    """顧客ビューのテスト"""

    def test_customer_index_requires_login(self, client):
        """顧客一覧ページの認証要求テスト"""
        response = client.get('/customers/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_customer_index_authenticated(self, authenticated_client, test_user):
        """認証済みユーザーの顧客一覧アクセステスト"""
        response = authenticated_client.get('/customers/')
        assert response.status_code == 200
        assert '顧客管理' in response.get_data(as_text=True)

    def test_customer_index_with_customers(self, authenticated_client, app):
        """顧客データありの一覧表示テスト"""
        with app.app_context():
            # テスト用顧客を作成
            customers = [
                Customer(first_name='太郎', last_name='田中', email='tanaka@example.com'),
                Customer(first_name='花子', last_name='佐藤', email='sato@example.com'),
                Customer(first_name='次郎', last_name='鈴木', email='suzuki@example.com')
            ]
            db.session.add_all(customers)
            db.session.commit()

        response = authenticated_client.get('/customers/')
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '田中 太郎' in response_text
        assert '佐藤 花子' in response_text
        assert '鈴木 次郎' in response_text

    def test_customer_index_search(self, authenticated_client, app):
        """顧客検索機能のテスト"""
        with app.app_context():
            customers = [
                Customer(first_name='太郎', last_name='田中', email='tanaka@example.com', company='株式会社A'),
                Customer(first_name='花子', last_name='佐藤', email='sato@example.com', company='株式会社B')
            ]
            db.session.add_all(customers)
            db.session.commit()

        # 名前での検索
        response = authenticated_client.get('/customers/?search=田中')
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '田中 太郎' in response_text
        assert '佐藤 花子' not in response_text

        # 会社名での検索
        response = authenticated_client.get('/customers/?search=株式会社B')
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '佐藤 花子' in response_text
        assert '田中 太郎' not in response_text

    def test_customer_create_get(self, authenticated_client):
        """顧客作成ページGETのテスト"""
        response = authenticated_client.get('/customers/create')
        assert response.status_code == 200
        assert '顧客新規登録' in response.get_data(as_text=True)

    def test_customer_create_post_valid(self, authenticated_client):
        """有効データでの顧客作成POSTテスト"""
        response = authenticated_client.post('/customers/create', data={
            'first_name': '太郎',
            'last_name': '田中',
            'email': 'create_test@example.com',
            'phone': '090-1234-5678',
            'company': '株式会社テスト'
        })

        assert response.status_code == 302  # リダイレクト

        # 作成された顧客の詳細ページにリダイレクトされる
        assert '/customers/' in response.location

    def test_customer_create_post_invalid(self, authenticated_client):
        """無効データでの顧客作成POSTテスト"""
        response = authenticated_client.post('/customers/create', data={
            'first_name': '',  # 必須フィールドが空
            'last_name': '田中',
            'email': 'invalid-email'  # 無効なメールアドレス
        })

        assert response.status_code == 200  # フォームエラーで同じページに戻る
        response_text = response.get_data(as_text=True)
        assert '名前を入力してください' in response_text

    def test_customer_view(self, authenticated_client, app):
        """顧客詳細表示のテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='view_test@example.com',
                phone='090-1234-5678',
                company='株式会社テスト'
            )
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id

        response = authenticated_client.get(f'/customers/{customer_id}')
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '田中 太郎' in response_text
        assert 'view_test@example.com' in response_text
        assert '090-1234-5678' in response_text

    def test_customer_view_not_found(self, authenticated_client):
        """存在しない顧客詳細のテスト"""
        response = authenticated_client.get('/customers/999999')
        assert response.status_code == 404

    def test_customer_edit_get(self, authenticated_client, app):
        """顧客編集ページGETのテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='edit_test@example.com'
            )
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id

        response = authenticated_client.get(f'/customers/{customer_id}/edit')
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '顧客情報編集' in response_text
        assert 'edit_test@example.com' in response_text

    def test_customer_edit_post_valid(self, authenticated_client, app):
        """有効データでの顧客編集POSTテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='edit_post_test@example.com'
            )
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id

        response = authenticated_client.post(f'/customers/{customer_id}/edit', data={
            'first_name': '次郎',  # 名前を変更
            'last_name': '田中',
            'email': 'edit_post_test@example.com',
            'phone': '090-9999-9999',  # 電話番号を追加
            'company': '更新株式会社'  # 会社名を追加
        })

        assert response.status_code == 302  # リダイレクト

    def test_customer_edit_inactive_customer(self, authenticated_client, app):
        """無効化された顧客の編集テスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='inactive_edit@example.com'
            )
            customer.deactivate()
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id

        response = authenticated_client.post(f'/customers/{customer_id}/edit', data={
            'first_name': '次郎',
            'last_name': '田中',
            'email': 'inactive_edit@example.com'
        })

        # サービス層リファクタリング後は、エラーメッセージと共に同じページに戻る（200）
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '無効化された顧客は編集できません' in response_text

    def test_customer_delete(self, authenticated_client, app):
        """顧客削除（無効化）のテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='delete_test@example.com'
            )
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id

        response = authenticated_client.post(f'/customers/{customer_id}/delete')
        assert response.status_code == 302  # リダイレクト

        # 顧客が無効化されていることを確認
        with app.app_context():
            customer = Customer.query.get(customer_id)
            assert customer.is_active == False

    def test_customer_activate(self, authenticated_client, app):
        """顧客有効化のテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='activate_test@example.com'
            )
            customer.deactivate()
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id

        response = authenticated_client.post(f'/customers/{customer_id}/activate')
        assert response.status_code == 302  # リダイレクト

        # 顧客が有効化されていることを確認
        with app.app_context():
            customer = Customer.query.get(customer_id)
            assert customer.is_active == True

    def test_customer_pagination(self, authenticated_client, app):
        """ページネーション機能のテスト"""
        with app.app_context():
            # 15件の顧客を作成（ページサイズは10）
            customers = []
            for i in range(15):
                customer = Customer(
                    first_name=f'太郎{i}',
                    last_name='田中',
                    email=f'pagination{i}@example.com'
                )
                customers.append(customer)
            db.session.add_all(customers)
            db.session.commit()

        # 1ページ目
        response = authenticated_client.get('/customers/')
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '次へ' in response_text  # 次ページリンクがある

        # 2ページ目
        response = authenticated_client.get('/customers/?page=2')
        assert response.status_code == 200
        response_text = response.get_data(as_text=True)
        assert '前へ' in response_text  # 前ページリンクがある

    def test_customer_routes_require_authentication(self, client):
        """すべての顧客ルートで認証が必要なことのテスト"""
        routes = [
            '/customers/',
            '/customers/create',
            '/customers/1',
            '/customers/1/edit',
        ]

        for route in routes:
            response = client.get(route)
            assert response.status_code == 302
            assert '/auth/login' in response.location

        # POSTルートのテスト
        post_routes = [
            ('/customers/create', {}),
            ('/customers/1/edit', {}),
            ('/customers/1/delete', {}),
            ('/customers/1/activate', {})
        ]

        for route, data in post_routes:
            response = client.post(route, data=data)
            assert response.status_code == 302
            assert '/auth/login' in response.location