# 店舗管理機能設計書

## 概要

Flask CRMシステムの店舗管理機能の詳細設計書です。本機能は、店舗の基本情報管理、営業状況の追跡、地域別分析などの機能を提供します。

## システム要件

### 機能要件

1. **店舗CRUD操作**
   - 店舗の作成・読取・更新・削除機能
   - 基本情報（名前、住所、連絡先）の管理
   - 営業状況（営業中、一時休業、休業）の管理

2. **営業時間管理**
   - 曜日別営業時間の設定
   - 定休日の管理
   - 営業ステータスの表示

3. **地域管理**
   - 都道府県・市区町村による分類
   - 地域別店舗検索・フィルタリング

4. **検索・フィルタリング**
   - 店舗名・住所による検索
   - 営業状況による絞り込み
   - 地域による絞り込み

5. **統計・分析**
   - 営業年数の自動計算
   - 地域別店舗分布
   - 営業状況別統計

### 非機能要件

- **性能**: 1000店舗までの管理に対応
- **拡張性**: パッケージベースアーキテクチャによる保守性
- **セキュリティ**: 認証必須、入力検証実装
- **ユーザビリティ**: 直感的なUI、レスポンシブデザイン

## アーキテクチャ設計

### パッケージ構造

```
store_management/
├── models/
│   └── store.py              # Storeエンティティ
├── services/
│   └── store_service.py      # ビジネスロジック
├── views/
│   └── store_views.py        # HTTPエンドポイント
├── templates/stores/
│   ├── index.html           # 店舗一覧
│   ├── view.html            # 店舗詳細
│   ├── create.html          # 店舗作成
│   └── edit.html            # 店舗編集
├── forms.py                 # フォーム定義
├── store_config.py          # 設定管理
└── tests/                   # テストスイート
```

### レイヤー構成

1. **プレゼンテーション層** (Views)
   - HTTPリクエスト処理
   - テンプレートレンダリング
   - フォームバリデーション

2. **ビジネスロジック層** (Services)
   - CRUD操作
   - 検索・フィルタリング
   - 統計計算

3. **データアクセス層** (Models)
   - データベースマッピング
   - リレーション定義
   - バリデーション

4. **設定管理層** (Config)
   - 環境変数管理
   - デフォルト値設定
   - 動的設定更新

## データベース設計

### テーブル定義

```sql
CREATE TABLE stores (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(120),
    business_hours JSON,
    closed_days VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    location_prefecture VARCHAR(50),
    location_city VARCHAR(100),
    establishment_date DATE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_name (name),
    INDEX idx_status (status),
    INDEX idx_prefecture (location_prefecture),
    INDEX idx_city (location_city)
);
```

### データ整合性

- **必須フィールド**: name, address
- **制約**: status ∈ {active, inactive, temporarily_closed}
- **インデックス**: 検索性能向上のため主要フィールドにインデックス

## API設計

### REST エンドポイント

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/stores/` | 店舗一覧（検索・フィルタ対応） |
| GET | `/stores/view/<id>` | 店舗詳細表示 |
| GET | `/stores/create` | 店舗作成フォーム |
| POST | `/stores/create` | 店舗作成処理 |
| GET | `/stores/edit/<id>` | 店舗編集フォーム |
| POST | `/stores/edit/<id>` | 店舗更新処理 |
| POST | `/stores/delete/<id>` | 店舗削除処理 |

### API エンドポイント

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/stores/search` | AJAX店舗検索 |
| GET | `/stores/api/cities/<prefecture>` | 都道府県別市区町村取得 |
| GET | `/stores/api/statistics` | 統計情報取得 |
| GET | `/stores/api/prefectures` | 都道府県一覧取得 |

## ビジネスロジック設計

### StoreService クラス

```python
class StoreService:
    # CRUD操作
    @staticmethod
    def create_store(name, address, **kwargs) -> Tuple[bool, Store, str]

    @staticmethod
    def update_store(store_id, **kwargs) -> Tuple[bool, Store, str]

    @staticmethod
    def delete_store(store_id) -> Tuple[bool, str]

    @staticmethod
    def get_store_by_id(store_id) -> Optional[Store]

    # 検索・フィルタリング
    @staticmethod
    def get_stores_with_pagination(**filters) -> Tuple[Pagination, int]

    @staticmethod
    def search_stores(term) -> List[Store]

    @staticmethod
    def get_stores_by_location(**location) -> List[Store]

    # 統計・分析
    @staticmethod
    def get_statistics() -> Dict[str, Any]

    @staticmethod
    def get_prefectures() -> List[str]

    @staticmethod
    def get_cities_by_prefecture(prefecture) -> List[str]
```

### 主要アルゴリズム

1. **営業年数計算**
   ```python
   business_years = (today - establishment_date).days / 365.25
   ```

2. **検索クエリ最適化**
   - インデックス活用
   - ILIKE による部分一致検索
   - N+1問題の回避

3. **ページネーション**
   - SQLAlchemyのpaginate機能活用
   - 効率的なカウントクエリ

## UI/UX設計

### 画面設計

1. **店舗一覧画面**
   - 統計ダッシュボード（総店舗数、営業状況別カウント）
   - 検索・フィルタリングフォーム
   - 店舗リスト（テーブル形式）
   - ページネーション

2. **店舗詳細画面**
   - 基本情報表示
   - 営業時間表（曜日別）
   - 営業年数・統計情報
   - 操作ボタン（編集・削除）

3. **店舗作成・編集画面**
   - 2カラムレイアウト
   - 営業時間入力（曜日別）
   - バリデーションメッセージ
   - デフォルト値設定機能

### レスポンシブデザイン

- Bootstrap 4フレームワーク使用
- モバイルファースト設計
- タブレット・デスクトップ対応

## セキュリティ設計

### 認証・認可

- Flask-Login による認証必須
- 全エンドポイントで `@login_required` デコレータ適用

### 入力検証

1. **サーバーサイド検証**
   - WTForms によるフォーム検証
   - 長さ制限、形式チェック
   - SQLインジェクション対策

2. **クライアントサイド検証**
   - HTML5 フォーム検証
   - JavaScript による追加検証

### データ保護

- CSRF トークン使用
- XSS 対策（テンプレートエスケープ）
- 適切な HTTP ヘッダー設定

## 設定管理設計

### StoreConfig クラス

```python
class StoreConfig(BaseConfig):
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'pagination': {'per_page': 20, 'max_per_page': 100},
            'search': {'min_length': 2, 'max_results': 1000},
            'validation': {'name_max_length': 200, 'address_max_length': 500},
            'business_hours': {'default_weekday_hours': '09:00-18:00'},
            'display': {'show_inactive_stores': True, 'show_statistics': True}
        }
```

### 環境変数

- `STORE_PAGINATION_PER_PAGE`: ページあたり表示件数
- `STORE_SEARCH_MIN_LENGTH`: 検索最小文字数
- `STORE_DEFAULT_MIN_STOCK`: デフォルト最小在庫

## テスト設計

### テスト戦略

1. **ユニットテスト**
   - モデル層: Store クラスの全メソッド
   - サービス層: StoreService の全メソッド
   - 設定層: StoreConfig の設定取得

2. **統合テスト**
   - ビュー層: 全HTTPエンドポイント
   - フォーム: バリデーション・データ処理
   - API: JSON レスポンス

3. **機能テスト**
   - CRUD操作の完全フロー
   - 検索・フィルタリング機能
   - 認証・認可の動作確認

### テストカバレッジ目標

- **モデル層**: 95%以上
- **サービス層**: 90%以上
- **ビュー層**: 80%以上

## 運用設計

### パフォーマンス

1. **データベース最適化**
   - 適切なインデックス設計
   - クエリ最適化
   - 接続プール使用

2. **キャッシュ戦略**
   - 統計情報のキャッシュ
   - 都道府県・市区町村データのキャッシュ

### 監視・ログ

1. **アプリケーションログ**
   - 店舗作成・更新・削除のログ
   - エラー発生時の詳細ログ

2. **メトリクス**
   - 店舗数の推移
   - 検索クエリの統計
   - エラー率の監視

## 拡張計画

### 短期拡張（次バージョン）

1. **機能拡張**
   - 店舗画像アップロード
   - 営業時間の詳細設定
   - 店舗間の距離計算

2. **UI/UX改善**
   - マップ表示機能
   - ダッシュボードの強化
   - CSVエクスポート機能

### 長期拡張

1. **外部連携**
   - Google Maps API 統合
   - 天気情報API連携
   - POS システム連携

2. **分析機能**
   - 売上データとの連携
   - 来客数分析
   - 地域別パフォーマンス分析

## 実装詳細

### 技術スタック

- **Backend**: Flask 2.0+, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 4, jQuery, Chart.js
- **Database**: SQLite (開発), MySQL (本番)
- **Testing**: pytest, Flask-Testing

### 依存関係

```python
# 主要依存関係
Flask>=2.0.0
SQLAlchemy>=1.4.0
Flask-Login>=0.6.0
Flask-WTF>=1.0.0
WTForms>=3.0.0
Flask-Migrate>=3.0.0
```

### デプロイメント

1. **開発環境**
   - SQLite データベース
   - Flask 開発サーバー
   - デバッグモード有効

2. **本番環境**
   - MySQL データベース
   - Gunicorn + Nginx
   - プロダクションモード

## まとめ

本設計書では、Flask CRMシステムの店舗管理機能について包括的な設計を行いました。パッケージベースアーキテクチャを採用し、拡張性と保守性を確保しています。また、適切なテスト戦略により品質を担保し、セキュリティ要件も満たしています。

この設計に基づいて実装された店舗管理機能は、既存の顧客管理・製品管理機能と統合され、完全なCRMシステムを構成します。