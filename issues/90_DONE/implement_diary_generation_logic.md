# 絵日記生成ワークフローの実装 (LangGraph)

## Summary
保存された会話ログを元に、LangGraph を使ったグラフベースのワークフローで絵日記を生成します。
Gemini で日記テキストを生成・品質チェックし、Imagen 3 で画像を生成、Firestore に保存します。

**設計詳細**: [docs/design.md - Section 5](../docs/design.md#5-絵日記生成ワークフロー-langgraph)

## Tasks

### セットアップ
- [x] `langgraph` を依存関係に追加 (`uv add langgraph`)
- [x] `src/diary_workflow.py` を作成

### ノード実装

#### extract_keywords (キーワード抽出)
- [x] Gemini API で会話ログから4つのキーワードを抽出
- [x] JSON形式でパース

#### generate_diary (日記生成)
- [x] Gemini API で「ぼくの夏休み」風の絵日記テキストを生成
- [x] 文字数制限（100-200文字程度）

#### check_quality (品質チェック)
- [x] Gemini API で生成文章を評価
- [x] 品質スコア (0.0 - 1.0) を返す
- [x] NG時のリトライロジック（最大3回）

#### generate_image (画像生成)
- [x] Imagen 3 API で絵日記用の画像を生成
- [x] Cloud Storage に保存
- [x] 依存関係追加 (`google-cloud-storage`)

#### save_result (結果保存)
- [x] Firestore ドキュメントを更新
    - `status`: `completed`
    - `diaryText`: 生成されたテキスト
    - `imageUrl`: 画像URL
    - `keywords`: 抽出されたキーワード

### グラフ構築
- [x] `StateGraph` で各ノードを接続
- [x] 条件分岐エッジの実装（品質チェック → リトライ or 画像生成）
- [x] フォールバック処理の実装

### API 連携
- [x] `POST /diaries` から LangGraph ワークフローを呼び出す
- [ ] 非同期実行 or バックグラウンドタスク化 → `async_diary_generation` issue に分離

### 動作確認
- [x] ローカル環境でのE2Eテスト
- [x] 品質チェック → リトライのフロー確認

## Notes
- `implement_diary_ingestion` の後続タスク
- Agentic ポイント: 自己評価ループ、条件分岐、フォールバック
- 非同期化は `async_diary_generation` issue で対応
