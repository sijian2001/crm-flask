import pytest
from forms import CustomerForm, CustomerSearchForm
from models import Customer, db

class TestCustomerForm:
    """顧客フォームのテスト"""

    def test_customer_form_valid_data(self, app):
        """有効なデータでのフォームテスト"""
        with app.app_context():
            form = CustomerForm(data={
                'first_name': '太郎',
                'last_name': '田中',
                'email': 'tanaka@example.com',
                'phone': '090-1234-5678',
                'company': '株式会社テスト',
                'address': '東京都渋谷区1-1-1',
                'notes': 'テスト顧客です'
            })

            assert form.validate()
            assert not form.errors

    def test_customer_form_minimal_data(self, app):
        """最小限のデータでのフォームテスト"""
        with app.app_context():
            form = CustomerForm(data={
                'first_name': '花子',
                'last_name': '佐藤',
                'email': 'sato@example.com'
            })

            assert form.validate()
            assert not form.errors

    def test_customer_form_missing_required_fields(self, app):
        """必須フィールド不足のテスト"""
        with app.app_context():
            # 名前なし
            form = CustomerForm(data={
                'last_name': '田中',
                'email': 'tanaka@example.com'
            })
            assert not form.validate()
            assert 'first_name' in form.errors

            # 姓なし
            form = CustomerForm(data={
                'first_name': '太郎',
                'email': 'tanaka@example.com'
            })
            assert not form.validate()
            assert 'last_name' in form.errors

            # メールアドレスなし
            form = CustomerForm(data={
                'first_name': '太郎',
                'last_name': '田中'
            })
            assert not form.validate()
            assert 'email' in form.errors

    def test_customer_form_invalid_email(self, app):
        """無効なメールアドレスのテスト"""
        with app.app_context():
            invalid_emails = [
                'invalid-email',
                '@example.com',
                'test@',
                'test@.com',
                'test..test@example.com'
            ]

            for invalid_email in invalid_emails:
                form = CustomerForm(data={
                    'first_name': '太郎',
                    'last_name': '田中',
                    'email': invalid_email
                })
                assert not form.validate()
                assert 'email' in form.errors

    def test_customer_form_field_length_limits(self, app):
        """フィールド長制限のテスト"""
        with app.app_context():
            # 名前が長すぎる
            form = CustomerForm(data={
                'first_name': 'a' * 51,  # 50文字制限
                'last_name': '田中',
                'email': 'test@example.com'
            })
            assert not form.validate()
            assert 'first_name' in form.errors

            # 姓が長すぎる
            form = CustomerForm(data={
                'first_name': '太郎',
                'last_name': 'a' * 51,  # 50文字制限
                'email': 'test@example.com'
            })
            assert not form.validate()
            assert 'last_name' in form.errors

            # メールアドレスが長すぎる
            form = CustomerForm(data={
                'first_name': '太郎',
                'last_name': '田中',
                'email': 'a' * 110 + '@example.com'  # 120文字制限
            })
            assert not form.validate()
            assert 'email' in form.errors

    def test_customer_form_email_uniqueness_new_customer(self, app):
        """新規顧客でのメールアドレス重複チェック"""
        with app.app_context():
            # 既存の顧客を作成
            existing_customer = Customer(
                first_name='既存',
                last_name='顧客',
                email='existing@example.com'
            )
            db.session.add(existing_customer)
            db.session.commit()

            # 同じメールアドレスで新規登録を試行
            form = CustomerForm(data={
                'first_name': '新規',
                'last_name': '顧客',
                'email': 'existing@example.com'
            })

            assert not form.validate()
            assert 'email' in form.errors
            assert 'このメールアドレスは既に使用されています。' in form.email.errors

    def test_customer_form_email_uniqueness_edit_customer(self, app):
        """既存顧客編集でのメールアドレス重複チェック"""
        with app.app_context():
            # 既存の顧客を作成
            customer1 = Customer(
                first_name='顧客1',
                last_name='テスト',
                email='customer1@example.com'
            )
            customer2 = Customer(
                first_name='顧客2',
                last_name='テスト',
                email='customer2@example.com'
            )
            db.session.add_all([customer1, customer2])
            db.session.commit()

            # 顧客1を編集して顧客2のメールアドレスに変更しようとする
            form = CustomerForm(customer=customer1, data={
                'first_name': '顧客1',
                'last_name': 'テスト',
                'email': 'customer2@example.com'
            })

            assert not form.validate()
            assert 'email' in form.errors

            # 顧客1を編集して同じメールアドレスのままにする（問題なし）
            form = CustomerForm(customer=customer1, data={
                'first_name': '顧客1更新',
                'last_name': 'テスト',
                'email': 'customer1@example.com'
            })

            assert form.validate()

    def test_customer_form_optional_fields(self, app):
        """オプションフィールドのテスト"""
        with app.app_context():
            # オプションフィールドが空でもOK
            form = CustomerForm(data={
                'first_name': '太郎',
                'last_name': '田中',
                'email': 'tanaka@example.com',
                'phone': '',
                'company': '',
                'address': '',
                'notes': ''
            })

            assert form.validate()

            # オプションフィールドに有効な値を設定
            form = CustomerForm(data={
                'first_name': '太郎',
                'last_name': '田中',
                'email': 'tanaka@example.com',
                'phone': '090-1234-5678',  # 有効な電話番号
                'company': '株式会社テスト',  # 有効な会社名
                'address': '東京都渋谷区1-1-1',  # 有効な住所
                'notes': '備考です'  # 有効な備考
            })

            assert form.validate()

class TestCustomerSearchForm:
    """顧客検索フォームのテスト"""

    def test_customer_search_form_valid(self, app):
        """有効な検索フォームのテスト"""
        with app.app_context():
            form = CustomerSearchForm(data={
                'search': '田中'
            })

            assert form.validate()

    def test_customer_search_form_empty(self, app):
        """空の検索フォームのテスト"""
        with app.app_context():
            form = CustomerSearchForm(data={
                'search': ''
            })

            assert form.validate()  # 空でもOK

    def test_customer_search_form_no_data(self, app):
        """データなしの検索フォームのテスト"""
        with app.app_context():
            form = CustomerSearchForm()

            assert form.validate()  # データなしでもOK