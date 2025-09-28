# 顧客管理機能設計書

## 概要
Flask CRMシステムの顧客管理機能の詳細設計書。認証システムで確立されたアーキテクチャパターンを踏襲し、一貫性のある実装を提供する。

## 機能要件

### 基本機能
- **顧客登録**: 新規顧客の情報登録
- **顧客一覧**: 登録済み顧客の一覧表示
- **顧客詳細**: 個別顧客の詳細情報表示
- **顧客編集**: 既存顧客情報の更新
- **顧客削除**: 顧客の論理削除（無効化）
- **顧客検索**: 名前・メール・会社名での検索
- **ページネーション**: 大量データの効率的表示

### 高度な機能
- **顧客有効化**: 無効化された顧客の復旧
- **検索フィルタ**: 複数条件での絞り込み
- **ソート機能**: 更新日時順での表示
- **レスポンシブUI**: モバイル対応インターface

## 技術設計

### アーキテクチャパターン
```
├── models.py          # データモデル（Customer）
├── forms.py           # WTFormsフォーム定義
├── customers.py       # Blueprintコントローラー
└── templates/customers/
    ├── index.html     # 顧客一覧
    ├── form.html      # 登録・編集フォーム
    └── view.html      # 顧客詳細
```

### データモデル設計

#### Customer Entity
```python
class Customer(db.Model):
    __tablename__ = 'customers'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Required Fields
    first_name = db.Column(db.String(50), nullable=False, index=True)
    last_name = db.Column(db.String(50), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    # Optional Fields
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    company = db.Column(db.String(100))
    notes = db.Column(db.Text)

    # System Fields
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

#### フィールド仕様
| フィールド | 型 | 制約 | 説明 |
|-----------|----|----- |-----|
| id | Integer | Primary Key | 自動採番ID |
| first_name | String(50) | Not Null, Index | 名前 |
| last_name | String(50) | Not Null, Index | 姓 |
| email | String(120) | Unique, Not Null, Index | メールアドレス |
| phone | String(20) | Optional | 電話番号 |
| address | Text | Optional | 住所 |
| company | String(100) | Optional | 会社名 |
| notes | Text | Optional | 備考 |
| is_active | Boolean | Default True | 有効フラグ |
| created_at | DateTime | Default Now | 作成日時 |
| updated_at | DateTime | Auto Update | 更新日時 |

### フォーム設計

#### BaseCustomerForm
共通フィールド（first_name, last_name, email）を定義し、DRY原則を実践。

#### CustomerForm
- **継承**: BaseCustomerFormを継承
- **追加フィールド**: phone, company, address, notes
- **バリデーション**: メールアドレス重複チェック（編集時は自身を除外）
- **レンダリング**: Bootstrap 5対応のHTML属性

#### CustomerSearchForm
- **検索フィールド**: 自由入力テキスト
- **対象**: 名前、メール、会社名を横断検索

### コントローラー設計

#### エンドポイント一覧
| メソッド | パス | 機能 | 認証 |
|---------|------|------|------|
| GET | `/customers/` | 顧客一覧 | Required |
| GET | `/customers/create` | 新規作成フォーム | Required |
| POST | `/customers/create` | 顧客登録処理 | Required |
| GET | `/customers/<id>` | 顧客詳細 | Required |
| GET | `/customers/<id>/edit` | 編集フォーム | Required |
| POST | `/customers/<id>/edit` | 更新処理 | Required |
| POST | `/customers/<id>/delete` | 削除（無効化） | Required |
| POST | `/customers/<id>/activate` | 有効化 | Required |
| GET | `/customers/search` | 検索リダイレクト | Required |

#### ビジネスロジック
```python
# 顧客一覧（ページネーション + 検索）
def index():
    query = Customer.query.filter_by(is_active=True)
    if search_term:
        query = query.filter(or_(
            Customer.first_name.ilike(f'%{search_term}%'),
            Customer.last_name.ilike(f'%{search_term}%'),
            Customer.email.ilike(f'%{search_term}%'),
            Customer.company.ilike(f'%{search_term}%')
        ))
    customers = query.order_by(Customer.updated_at.desc()).paginate(...)
```

### セキュリティ設計

#### 認証・認可
- **全エンドポイント**: `@login_required`デコレーターで保護
- **セッション管理**: Flask-Loginによる統合認証
- **CSRF保護**: Flask-WTFによる自動保護

#### 入力検証
- **フォームレベル**: WTFormsバリデーター
- **データベースレベル**: 制約とインデックス
- **ビジネスレベル**: カスタムバリデーション

#### ログ・監査
```python
# セキュリティイベントのログ記録
logger.info(f'Customer {customer.full_name} created by user {current_user.username}')
logger.info(f'Customer {customer.full_name} updated by user {current_user.username}')
logger.info(f'Customer {customer.full_name} deactivated by user {current_user.username}')
```

### UI/UX設計

#### デザインシステム
- **フレームワーク**: Bootstrap 5.1.3
- **アイコン**: Font Awesome 6.0.0
- **カラーパレット**: 既存システムと統一
- **レスポンシブ**: モバイルファースト設計

#### ユーザーフロー
1. **ダッシュボード** → 顧客管理リンク
2. **顧客一覧** → 検索・新規作成・詳細表示
3. **顧客詳細** → 編集・削除・一覧戻り
4. **フォーム** → バリデーション・成功メッセージ

#### インタラクション
- **Flash Messages**: 操作結果の即座フィードバック
- **確認ダイアログ**: 削除操作の安全確認
- **フォームエラー**: インライン表示とスタイリング

### パフォーマンス設計

#### データベース最適化
- **インデックス**: first_name, last_name, email, is_active
- **ページネーション**: `paginate(page=page, per_page=10)`
- **絞り込みクエリ**: `filter_by(is_active=True)`で論理削除対応

#### フロントエンド最適化
- **CDN**: Bootstrap/FontAwesome外部リンク
- **遅延読み込み**: 大量データ時のページネーション
- **キャッシュ**: 静的アセットの効率的配信

## テスト設計

### テストカバレッジ
- **モデルテスト**: 11テストケース（CRUD、バリデーション、ビジネスロジック）
- **フォームテスト**: 11テストケース（入力検証、重複チェック）
- **ビューテスト**: 15テストケース（認証、CRUD、ページネーション）

### テスト分類
1. **Unit Tests**: 個別コンポーネントの動作検証
2. **Integration Tests**: エンドポイント統合テスト
3. **Security Tests**: 認証・入力検証テスト

### テストデータ
- **Fixture**: 共通テストデータの定義
- **Factory**: 動的テストデータ生成
- **Cleanup**: テスト間のデータ分離

## 運用設計

### エラーハンドリング
```python
try:
    db.session.add(customer)
    db.session.commit()
    logger.info(f'Customer created: {customer.full_name}')
except IntegrityError:
    db.session.rollback()
    logger.error(f'Integrity error during customer creation')
    flash('メールアドレスが重複しています', 'error')
except Exception as e:
    db.session.rollback()
    logger.error(f'Unexpected error: {str(e)}')
    flash('予期しないエラーが発生しました', 'error')
```

### 監視・ログ
- **アクセスログ**: 顧客データアクセスの記録
- **操作ログ**: CRUD操作の監査証跡
- **エラーログ**: 例外とエラーの詳細記録

### バックアップ・復旧
- **論理削除**: データ完全性の保持
- **更新履歴**: updated_atフィールドによる変更追跡
- **復旧機能**: 無効化顧客の有効化オプション

## 今後の拡張計画

### Phase 2: 関連機能
- **注文管理**: 顧客と注文の関連付け
- **サポート履歴**: 顧客サポート記録
- **コミュニケーション履歴**: メール・電話対応記録

### Phase 3: 高度な機能
- **顧客セグメンテーション**: 属性別グループ化
- **レポート機能**: 顧客分析とダッシュボード
- **外部API連携**: CRM外部システム統合

### Phase 4: エンタープライズ機能
- **権限管理**: 部門別アクセス制御
- **ワークフロー**: 承認プロセス
- **API**: RESTful API提供

## まとめ
顧客管理機能は、既存の認証システムアーキテクチャを継承し、拡張性・保守性・セキュリティを重視した設計となっている。77個のテストケースによる包括的品質保証と、Bootstrap 5によるモダンなUIにより、エンタープライズグレードのCRMシステムの基盤として機能する。