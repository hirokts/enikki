# 会話ログの受信と保存 (Ingestion)

## Summary
フロントエンドから会話ログを受信し、Firestore に「生の会話ログ」として保存する API と、フロントエンドの送信処理を実装します。
絵日記生成処理の前段階となる、データの受け皿を作ります。

## Tasks

### バックエンド実装 (API)
- [x] Pydanticモデルを作成（`src/models.py`）
    - `ConversationLogRequest`: 会話ログのリクエストボディ
- [x] Firestore クライアントの設定
    - 依存関係確認 (`google-cloud-firestore`)
- [x] `POST /diaries` エンドポイントを作成
    - 会話ログを受け取る
    - API Key認証を適用
    - **Firestoreに保存する**（ステータス: `pending`）
    - 生成された Document ID をレスポンスで返す

### フロントエンド実装 (Web)
- [x] API クライアントの拡張 (`src/lib/api.ts`)
    - `createDiary(log: any)` メソッドの追加
- [x] `MultimodalRecorder.svelte` の修正
    - 会話終了時 (`report_diary_event` ツールコール時) に バックエンド API を呼び出す
    - 成功時に画面遷移または完了メッセージ表示

### 動作確認
- [x] ローカル環境でのデータフロー確認
    - マイクで会話 -> 会話終了 -> Firestore にデータが作成されること

## Notes
- 生成ロジックは別課題 `implement_diary_generation_logic.md` で実施


## Notes
- **参考**: kickoff.md L375-378, L347-351
- **認証**: 既存の `/auth/token` エンドポイントと同様に、`X-API-Key` ヘッダーによる認証が必要

### リクエスト例
```bash
curl -X POST http://localhost:8000/diaries \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "messages": [
      {"role": "user", "content": "今日は公園に行ったよ"},
      {"role": "assistant", "content": "楽しかったですね！何をしましたか？"},
      {"role": "user", "content": "ブランコに乗って、アイスクリームを食べた"}
    ]
  }'
```

### レスポンス例
```json
{
  "diaryId": "abc123",
  "keywords": ["公園", "ブランコ", "アイス", "楽しい"],
  "text": "今日は公園に行きました。ブランコに乗って、とても楽しかったです。あつかったので、つめたいアイスクリームを食べました。おいしかったです。",
  "imageUrl": "https://storage.googleapis.com/enikki-cloud-enikki-images/abc123.png",
  "createdAt": "2026-01-31T15:30:00Z"
}
```

- 処理フロー:
  1. フロントエンドから `POST /diaries` で会話ログを受信
  2. Gemini で4単語抽出
  3. その4単語を元に絵日記テキスト生成
  4. テキストを元に Imagen 3 で画像生成
  5. Cloud Storage に画像保存
  6. Firestore に日記データを保存
  7. フロントエンドにレスポンス返却

- **依存ライブラリ**:
  - `google-cloud-aiplatform>=1.134.0` (Gemini, Imagen)
  - `google-cloud-firestore>=2.23.0`
  - `google-cloud-storage>=2.19.0` (新規追加が必要)

- **環境変数**:
  - `GCS_BUCKET_NAME`: Cloud Storageバケット名（例: `enikki-cloud-enikki-images`）
  - `GCP_PROJECT_ID`: GCPプロジェクトID
  - `GOOGLE_APPLICATION_CREDENTIALS`: サービスアカウントキーのパス（ローカル開発時）
  - `API_KEY`: API認証キー

- **将来の拡張**:
  - Notion や Slack への通知連携
  - バックグラウンドタスクキュー（Cloud Tasks）の利用
  - ユーザー認証との統合
