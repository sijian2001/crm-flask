# Customer Configuration Management

このドキュメントでは、Flask CRMシステムの顧客管理機能における設定管理について説明します。

## 概要

CustomerConfigクラスとFlask設定の統合により、ハードコードされた値を排除し、柔軟で保守性の高い設定管理を実現しています。

## CustomerConfigクラス

### 主要な設定項目

```python
from customer_config import CustomerConfig

# ページネーション設定
ITEMS_PER_PAGE = 10          # 1ページあたりの表示件数
MAX_ITEMS_PER_PAGE = 100     # 最大表示件数

# 検索フィールド設定
SEARCH_FIELDS = ['first_name', 'last_name', 'email', 'company']

# フィールド長制限（データベース制約と一致）
FIELD_LIMITS = {
    'first_name': 50,
    'last_name': 50,
    'email': 120,
    'phone': 20,
    'company': 100,
    'notes': 1000
}

# セキュリティ設定
ENABLE_AUDIT_LOG = True      # 監査ログの有効化
LOG_CUSTOMER_ACCESS = True   # 顧客アクセスログ
```

## Flask設定との統合

### config.py での設定

```python
# config.py
class Config:
    # 顧客管理設定
    CUSTOMER_ITEMS_PER_PAGE = int(os.environ.get('CUSTOMER_ITEMS_PER_PAGE') or 10)
    CUSTOMER_SEARCH_FIELDS = ['first_name', 'last_name', 'email', 'company']
    CUSTOMER_ENABLE_AUDIT_LOG = os.environ.get('CUSTOMER_ENABLE_AUDIT_LOG', 'True').lower() == 'true'

    # フィールド制限
    CUSTOMER_FIELD_LIMITS = {
        'first_name': 50,
        'last_name': 50,
        'email': 120,
        'phone': 20,
        'company': 100,
        'notes': 1000
    }
```

### 環境変数での設定

```bash
# 本番環境での設定例
export CUSTOMER_ITEMS_PER_PAGE=20
export CUSTOMER_ENABLE_AUDIT_LOG=true
```

## 使用方法

### コントローラーでの使用

```python
# customers.py
from flask import current_app
from customer_config import CustomerConfig

@customers.route('/')
@login_required
def index():
    per_page = CustomerConfig.get_items_per_page(current_app.config)

    customers_paginated = CustomerService.get_customers_with_pagination(
        page=page,
        per_page=per_page,
        search=search
    )
```

### サービス層での使用

```python
# services/customer_service.py
@staticmethod
def get_customers_with_pagination(page: int = 1, per_page: Optional[int] = None, search: Optional[str] = None):
    if per_page is None:
        per_page = CustomerConfig.get_items_per_page(current_app.config)

    if search:
        search_fields = CustomerConfig.get_search_fields(current_app.config)
        # 動的に検索条件を構築
```

### フォームでの使用

```python
# forms.py
from customer_config import CustomerConfig

class BaseCustomerForm(FlaskForm):
    first_name = StringField(
        '名前',
        validators=[
            DataRequired(message='名前を入力してください'),
            Length(min=1, max=CustomerConfig.FIELD_LIMITS['first_name'])
        ]
    )
```

## 設定値のオーバーライド

### 1. 環境変数によるオーバーライド

```bash
# 開発環境
export CUSTOMER_ITEMS_PER_PAGE=5

# 本番環境
export CUSTOMER_ITEMS_PER_PAGE=25
export CUSTOMER_ENABLE_AUDIT_LOG=true
```

### 2. Flask設定によるオーバーライド

```python
# テスト環境での設定
app.config['CUSTOMER_ITEMS_PER_PAGE'] = 3
app.config['CUSTOMER_SEARCH_FIELDS'] = ['first_name', 'email']
```

### 3. アプリケーション実行時の設定

```python
# 特定の環境でのカスタマイズ
if app.config.get('TESTING'):
    app.config['CUSTOMER_ITEMS_PER_PAGE'] = 5
```

## 設定値の取得方法

### 1. 基本的な取得

```python
# デフォルト値を使用
items_per_page = CustomerConfig.get_items_per_page()

# Flask設定を考慮
items_per_page = CustomerConfig.get_items_per_page(current_app.config)
```

### 2. 検索フィールドの動的取得

```python
search_fields = CustomerConfig.get_search_fields(current_app.config)

# 検索条件の動的構築
search_conditions = []
for field in search_fields:
    if hasattr(Customer, field):
        search_conditions.append(
            getattr(Customer, field).ilike(search_term)
        )
```

### 3. フィールド制限の取得

```python
# 特定フィールドの制限取得
max_length = CustomerConfig.get_field_limit('first_name', current_app.config)

# バリデーション用メッセージ生成
message = f'名前は{max_length}文字以下で入力してください'
```

## テストでの使用

### 設定をオーバーライドしたテスト

```python
def test_pagination_uses_config(self, app):
    with app.app_context():
        # テスト用設定
        app.config['CUSTOMER_ITEMS_PER_PAGE'] = 5

        result = CustomerService.get_customers_with_pagination(page=1)
        assert len(result.items) == 5  # 設定値が使用される
```

### 検索フィールドのカスタマイズテスト

```python
def test_search_fields_uses_config(self, app):
    with app.app_context():
        # 検索対象をfirst_nameとemailのみに限定
        app.config['CUSTOMER_SEARCH_FIELDS'] = ['first_name', 'email']

        # companyフィールドでの検索がヒットしないことを確認
        result = CustomerService.get_customers_with_pagination(search='会社名')
        assert len(result.items) == 0
```

## ベストプラクティス

### 1. デフォルト値の提供

- 常にフォールバック値を提供
- 環境依存しない動作を保証

### 2. 型安全性

- メソッドで適切な型ヒントを提供
- 設定値の妥当性検証

### 3. ドキュメント化

- 設定項目の用途を明確に記述
- 制約値とデータベーススキーマの整合性確保

### 4. テストカバレッジ

- 設定値の変更が与える影響をテスト
- デフォルト値とカスタム値の両方をテスト

## 拡張計画

今後の機能拡張において、以下の設定項目を追加予定：

- エクスポート機能の設定
- 電話番号フォーマット検証
- メールドメイン検証
- キャッシュ設定
- パフォーマンス調整パラメータ

この設定管理システムにより、環境に応じた柔軟なカスタマイズと、保守性の高いコード管理を実現しています。