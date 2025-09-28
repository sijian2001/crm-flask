import pytest
from datetime import datetime
from models import Customer, db
from sqlalchemy.exc import IntegrityError

class TestCustomerModel:
    """顧客モデルのテスト"""

    def test_customer_creation(self, app):
        """顧客作成のテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='tanaka@example.com',
                phone='090-1234-5678',
                company='株式会社テスト',
                address='東京都渋谷区1-1-1',
                notes='テスト顧客です'
            )

            assert customer.first_name == '太郎'
            assert customer.last_name == '田中'
            assert customer.email == 'tanaka@example.com'
            assert customer.phone == '090-1234-5678'
            assert customer.company == '株式会社テスト'
            assert customer.address == '東京都渋谷区1-1-1'
            assert customer.notes == 'テスト顧客です'
            assert customer.is_active == True
            assert isinstance(customer.created_at, datetime)
            assert isinstance(customer.updated_at, datetime)

    def test_customer_minimal_creation(self, app):
        """最小限の情報での顧客作成テスト"""
        with app.app_context():
            customer = Customer(
                first_name='花子',
                last_name='佐藤',
                email='sato@example.com'
            )

            assert customer.first_name == '花子'
            assert customer.last_name == '佐藤'
            assert customer.email == 'sato@example.com'
            assert customer.phone is None
            assert customer.company is None
            assert customer.address is None
            assert customer.notes is None
            assert customer.is_active == True

    def test_customer_full_name(self, app):
        """フルネームプロパティのテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='tanaka@example.com'
            )

            assert customer.full_name == '田中 太郎'

    def test_customer_update_info(self, app):
        """顧客情報更新のテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='tanaka@example.com'
            )

            original_updated_at = customer.updated_at

            # 少し時間を置く
            import time
            time.sleep(0.01)

            customer.update_info(
                first_name='次郎',
                company='株式会社更新',
                notes='更新されました'
            )

            assert customer.first_name == '次郎'
            assert customer.last_name == '田中'  # 変更されていない
            assert customer.company == '株式会社更新'
            assert customer.notes == '更新されました'
            assert customer.updated_at > original_updated_at

    def test_customer_deactivate(self, app):
        """顧客無効化のテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='tanaka@example.com'
            )

            assert customer.is_active == True

            customer.deactivate()

            assert customer.is_active == False

    def test_customer_activate(self, app):
        """顧客有効化のテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='tanaka@example.com'
            )

            customer.deactivate()
            assert customer.is_active == False

            customer.activate()
            assert customer.is_active == True

    def test_customer_persistence(self, app):
        """顧客データの永続化テスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='persistence@example.com'
            )

            db.session.add(customer)
            db.session.commit()

            # IDが割り当てられている
            assert customer.id is not None

            # データベースから取得
            retrieved_customer = Customer.query.filter_by(email='persistence@example.com').first()
            assert retrieved_customer is not None
            assert retrieved_customer.full_name == '田中 太郎'

    def test_customer_unique_email(self, app):
        """メールアドレス一意制約のテスト"""
        with app.app_context():
            customer1 = Customer(
                first_name='太郎',
                last_name='田中',
                email='unique@example.com'
            )

            customer2 = Customer(
                first_name='花子',
                last_name='佐藤',
                email='unique@example.com'  # 同じメールアドレス
            )

            db.session.add(customer1)
            db.session.commit()

            db.session.add(customer2)

            # 一意制約違反でエラーが発生
            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_customer_repr(self, app):
        """文字列表現のテスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='repr@example.com'
            )

            assert repr(customer) == '<Customer 田中 太郎>'

    def test_customer_update_info_protected_fields(self, app):
        """保護されたフィールドの更新テスト"""
        with app.app_context():
            customer = Customer(
                first_name='太郎',
                last_name='田中',
                email='protected@example.com'
            )

            original_id = customer.id
            original_created_at = customer.created_at

            # 保護されたフィールドの更新を試行
            customer.update_info(
                id=999,  # 変更されないはず
                created_at=datetime(2020, 1, 1),  # 変更されないはず
                first_name='次郎'
            )

            assert customer.id == original_id
            assert customer.created_at == original_created_at
            assert customer.first_name == '次郎'  # これは更新される