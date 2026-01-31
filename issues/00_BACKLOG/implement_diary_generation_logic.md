# 絵日記生成ロジックの実装（Gemini & Imagen）

## Summary
保存された会話ログを元に、Gemini で日記テキストを生成し、Imagen 3 で画像を生成するバックエンドロジックを実装します。

## Tasks

### 4単語抽出
- [ ] Gemini APIを使って会話ログから重要な4単語を抽出
    - プロンプト設計（「この会話から絵日記に使う4つのキーワードを抽出してください」など）
    - 抽出結果の構造化（JSON形式）

### 日記文章生成
- [ ] Gemini APIで「ぼくの夏休み」風の絵日記テキストを生成
    - 抽出した4単語を元にプロンプト構築
    - 子供らしい文体、感情表現を含める
    - 文字数制限（100-200文字程度）

### 画像生成 & 保存
- [ ] 画像生成プロンプトの作成
- [ ] Imagen 3 APIで絵日記用の画像を生成
- [ ] Cloud Storage への保存処理実装
    - 依存関係追加 (`google-cloud-storage`)

### トランザクション・状態管理
- [ ] 生成ステータスの管理
    - Firestore ドキュメントの更新 (`status: 'completed'`, `imageUrl`, `diaryText` 等)
- [ ] エラーハンドリング
    - 生成失敗時のステータス更新 (`status: 'failed'`)

## Notes
- `implement_diary_ingestion` の後続タスク
- Cloud Functions (Eventarc) ではなく、まずはシンプルに Fast API 内で処理（同期またはバックグラウンドタスク）する想定
