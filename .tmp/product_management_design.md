# 製品管理機能設計書

## 概要

Flask CRMシステムの製品管理機能の実装設計書です。顧客管理機能と同様のアーキテクチャパターンを採用し、一貫性のある開発アプローチを実現しています。

## アーキテクチャ

### システム構成

```
製品管理システム
├── データモデル層 (models.py)
│   ├── Product モデル
│   └── Category モデル
├── サービス層 (services/product_service.py)
│   ├── ProductService
│   └── CategoryService
├── 設定管理 (product_config.py)
├── フォーム層 (forms.py)
│   ├── ProductForm
│   ├── CategoryForm
│   └── 検索フォーム各種
├── ビュー層 (products.py)
│   ├── 製品CRUD操作
│   ├── カテゴリ管理
│   └── 在庫管理
└── テンプレート層 (templates/products/)
    ├── 製品管理画面
    ├── カテゴリ管理画面
    └── 在庫管理画面
```

## データモデル設計

### Category モデル

#### フィールド構成
- `id`: 主キー (Integer)
- `name`: カテゴリ名 (String(100), NOT NULL, インデックス)
- `description`: 説明 (Text, NULL可)
- `parent_id`: 親カテゴリID (Integer, FK, NULL可)
- `is_active`: アクティブフラグ (Boolean, デフォルト True)
- `created_at`: 作成日時 (DateTime, NOT NULL)
- `updated_at`: 更新日時 (DateTime, NOT NULL)

#### リレーションシップ
- **自己参照関係**: 階層カテゴリ対応
  - `children`: 子カテゴリ一覧
  - `parent`: 親カテゴリ
- **製品との関係**: One-to-Many
  - `products`: このカテゴリの製品一覧

#### ビジネスロジック
- `full_path`: 階層パスの取得（例: "電子機器 > スマートフォン"）
- `product_count`: アクティブな製品数の取得
- `get_all_children()`: 再帰的な子カテゴリ取得
- `deactivate()` / `activate()`: 状態管理

### Product モデル

#### フィールド構成
- `id`: 主キー (Integer)
- `name`: 製品名 (String(200), NOT NULL, インデックス)
- `description`: 説明 (Text, NULL可)
- `sku`: SKU (String(50), UNIQUE, NOT NULL, インデックス)
- `price`: 価格 (Numeric(10,2), NOT NULL)
- `cost`: 原価 (Numeric(10,2), NULL可)
- `stock_quantity`: 在庫数量 (Integer, デフォルト 0)
- `min_stock_level`: 最小在庫レベル (Integer, デフォルト 0)
- `category_id`: カテゴリID (Integer, FK, NOT NULL)
- `is_active`: アクティブフラグ (Boolean, デフォルト True)
- `created_at`: 作成日時 (DateTime, NOT NULL)
- `updated_at`: 更新日時 (DateTime, NOT NULL)

#### リレーションシップ
- **カテゴリとの関係**: Many-to-One
  - `category`: 所属カテゴリ

#### ビジネスロジック
- `is_low_stock`: 在庫不足判定
- `profit_margin`: 利益率計算
- `profit_amount`: 利益額計算
- `update_stock()`: 在庫数量更新
- `add_stock()` / `reduce_stock()`: 在庫増減
- `update_info()`: 製品情報更新
- `deactivate()` / `activate()`: 状態管理

## サービス層設計

### ProductService

#### 主要メソッド

1. **データ取得**
   - `get_products_with_pagination()`: ページネーション付き製品取得
   - `get_product_by_id()`: ID指定製品取得
   - `get_product_by_sku()`: SKU指定製品取得
   - `get_low_stock_products()`: 在庫不足製品取得

2. **データ操作**
   - `create_product()`: 製品作成
   - `update_product()`: 製品更新
   - `deactivate_product()` / `activate_product()`: 状態変更
   - `update_stock()`: 在庫更新

3. **検索・フィルタリング**
   - 製品名、SKU、説明での部分一致検索
   - カテゴリフィルタリング
   - 在庫不足フィルタリング
   - ソート機能（名前、価格、在庫数量）

### CategoryService

#### 主要メソッド

1. **データ取得**
   - `get_categories_with_pagination()`: ページネーション付きカテゴリ取得
   - `get_category_by_id()`: ID指定カテゴリ取得
   - `get_root_categories()`: ルートカテゴリ取得

2. **データ操作**
   - `create_category()`: カテゴリ作成
   - `update_category()`: カテゴリ更新
   - `deactivate_category()`: カテゴリ無効化

3. **階層管理**
   - 循環参照チェック
   - 深度制限チェック
   - 子カテゴリ取得

## 設定管理設計

### ProductConfig クラス

#### 設定カテゴリ

1. **ページネーション設定**
   - `per_page`: デフォルト20件
   - `max_per_page`: 最大100件
   - `orphans`: 最終ページ最小件数3件

2. **検索設定**
   - `min_length`: 最小検索文字数2文字
   - `max_results`: 最大検索結果1000件
   - `search_fields`: 検索対象フィールド

3. **バリデーション設定**
   - フィールド長制限
   - 価格・在庫の数値制限
   - SKU形式制限

4. **在庫管理設定**
   - `default_min_stock_level`: デフォルト最小在庫5個
   - `low_stock_warning_threshold`: 警告閾値10個
   - `auto_reorder_enabled`: 自動発注設定

5. **カテゴリ設定**
   - `max_depth`: 最大階層深度5階層
   - `allow_empty_categories`: 空カテゴリ許可

## フォーム設計

### 継承構造

```
FlaskForm
├── BaseCategoryForm
│   └── CategoryForm
├── BaseProductForm
│   └── ProductForm
├── ProductSearchForm
├── CategorySearchForm
└── StockUpdateForm
```

### バリデーション機能

1. **製品フォーム**
   - SKU重複チェック
   - カテゴリ存在確認
   - 価格・在庫の数値検証
   - SKU形式検証（英数字、ハイフン、アンダースコア）

2. **カテゴリフォーム**
   - 親カテゴリ存在確認
   - 循環参照防止
   - 階層深度制限

## ビュー設計

### URL構造

```
/products/
├── GET    /                      # 製品一覧
├── GET    /create                # 製品作成画面
├── POST   /create                # 製品作成処理
├── GET    /<id>                  # 製品詳細
├── GET    /<id>/edit             # 製品編集画面
├── POST   /<id>/edit             # 製品編集処理
├── POST   /<id>/delete           # 製品削除（無効化）
├── POST   /<id>/activate         # 製品有効化
├── GET    /<id>/update_stock     # 在庫更新画面
├── POST   /<id>/update_stock     # 在庫更新処理
├── GET    /categories/           # カテゴリ一覧
├── GET    /categories/create     # カテゴリ作成画面
├── POST   /categories/create     # カテゴリ作成処理
├── GET    /categories/<id>       # カテゴリ詳細
├── GET    /categories/<id>/edit  # カテゴリ編集画面
├── POST   /categories/<id>/edit  # カテゴリ編集処理
└── POST   /categories/<id>/delete # カテゴリ削除（無効化）
```

### 認証・認可

- 全ての製品管理機能は認証必須（`@login_required`）
- 無効化された製品・カテゴリの編集制限
- 製品が存在するカテゴリの無効化制限

## UI/UX設計

### デザインシステム

1. **Bootstrap 5ベース**
   - レスポンシブデザイン
   - 一貫したコンポーネント使用
   - アイコン表示（Font Awesome）

2. **ナビゲーション**
   - トップナビゲーションに製品管理リンク
   - 製品・カテゴリ間の相互遷移
   - パンくずナビゲーション

3. **データ表示**
   - ページネーション対応テーブル
   - ソート機能
   - 検索・フィルタリング
   - 在庫状況の視覚的表示

4. **フォーム**
   - リアルタイムバリデーション
   - 分かりやすいエラーメッセージ
   - 階層カテゴリ選択UI

## エラーハンドリング設計

### エラーハンドリング戦略

1. **utils/error_handlers.py活用**
   - 顧客管理と同じエラーハンドリングユーティリティを再利用
   - 一貫したエラーメッセージとログ出力

2. **ログ機能**
   - 操作ログの自動記録
   - エラー詳細の記録
   - ユーザー操作履歴

3. **ユーザーフィードバック**
   - Flashメッセージでの結果通知
   - 成功・エラーの明確な区別
   - 次のアクションの案内

## テスト設計

### テストカバレッジ

1. **単体テスト**
   - `test_product_models.py`: モデル機能テスト（25テストケース）
   - `test_product_service.py`: サービス層テスト（20テストケース）
   - `test_product_config.py`: 設定管理テスト（15テストケース）
   - `test_product_forms.py`: フォームテスト（18テストケース）

2. **統合テスト**
   - `test_product_views.py`: ビューレイヤーテスト（22テストケース）
   - 認証テスト
   - エンドポイントテスト

3. **テストデータ**
   - フィクスチャによるテストデータ作成
   - 階層カテゴリのテスト
   - 在庫管理のテスト

### テスト環境

- pytest使用
- SQLiteインメモリデータベース
- CSRFトークン無効化
- 認証モック

## パフォーマンス考慮事項

### データベース最適化

1. **インデックス設計**
   - 製品名、SKUにインデックス
   - カテゴリ名にインデックス
   - 外部キーインデックス

2. **クエリ最適化**
   - ページネーション使用
   - 必要なフィールドのみ取得
   - N+1問題の回避

3. **キャッシュ戦略**
   - 設定情報のキャッシュ
   - カテゴリ階層のキャッシュ

## セキュリティ考慮事項

### データ保護

1. **入力検証**
   - WTFormsによるバリデーション
   - SQLインジェクション対策
   - XSS対策

2. **認証・認可**
   - Flask-Loginによる認証
   - セッション管理
   - CSRF保護

3. **データ整合性**
   - トランザクション管理
   - 制約によるデータ保護
   - ソフトデリート

## 拡張性考慮事項

### 将来的な機能追加

1. **製品機能拡張**
   - 製品画像管理
   - バリエーション管理（サイズ、色など）
   - 製品レビュー機能

2. **在庫管理拡張**
   - 入出庫履歴
   - 自動発注機能
   - 在庫予測

3. **カテゴリ機能拡張**
   - カテゴリ属性管理
   - カテゴリテンプレート
   - 動的カテゴリ

### アーキテクチャ拡張

1. **マイクロサービス対応**
   - サービス層の独立化
   - API化対応
   - データベース分離

2. **多言語対応**
   - 国際化（i18n）
   - 製品名の多言語化
   - カテゴリの多言語化

## 運用・保守

### 監視項目

1. **パフォーマンス監視**
   - データベースクエリ性能
   - ページ応答時間
   - 検索性能

2. **ビジネス監視**
   - 製品登録数推移
   - 在庫状況監視
   - エラー発生率

### バックアップ戦略

1. **データバックアップ**
   - 製品データの定期バックアップ
   - カテゴリ構造の保存
   - 在庫履歴の保管

2. **設定バックアップ**
   - 製品設定の保存
   - カテゴリ設定の保存

## まとめ

本製品管理機能は、既存の顧客管理機能と一貫したアーキテクチャパターンを採用することで、以下の利点を実現しています：

1. **一貫性**: 同じデザインパターンによる保守性向上
2. **拡張性**: サービス層による機能拡張の容易性
3. **テスト容易性**: 包括的なテストカバレッジ
4. **ユーザビリティ**: 直感的なUI/UX設計
5. **保守性**: 明確な責務分離と設定管理

この設計により、スケーラブルで保守性の高い製品管理システムが実現されています。