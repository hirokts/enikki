# create_vertexai_token_endpoint

## Summary
フロントエンドが Vertex AI (Multimodal Live API) に直接接続するためのアクセストークンを発行するエンドポイントを実装する。
フロントエンドからバックエンドにリクエストし、バックエンドがサービスアカウント権限で短期トークンを生成して返却する。

## Tasks
- [ ] `POST /auth/token` エンドポイントの実装
    - Google Cloud の認証情報を使用してアクセストークンを生成
    - トークンの有効期限を設定（例：1時間）
    - トークンとプロジェクトID、リージョンを含むレスポンスを返却
- [ ] 認証ロジックの実装
    - `google-auth` ライブラリを使用
    - サービスアカウントのデフォルト認証情報を利用
    - 必要なスコープ: `https://www.googleapis.com/auth/cloud-platform` または `https://www.googleapis.com/auth/aiplatform`
- [ ] **CORS設定の追加**
    - `FastAPI.middleware.cors` を使用
    - フロントエンドのオリジン（開発時は `http://localhost:5173` 等）を許可
- [ ] 環境変数の追加
    - `GCP_PROJECT_ID`: プロジェクトID
    - `GCP_REGION`: リージョン（例: `us-central1`）
- [ ] ローカルでの動作確認
    - `GOOGLE_APPLICATION_CREDENTIALS` でサービスアカウントキーを指定
    - `curl` でトークン取得をテスト

## Notes
- **セキュリティ**: 本番環境では、トークン発行前にユーザー認証を追加すること（今回のスコープ外）
- **参考**: kickoff.md L340-345 に記載の設計に基づく
- トークンはフロントエンドで `@google-cloud/vertexai` SDK に渡して Gemini と接続する
- レスポンス例:
  ```json
  {
    "accessToken": "ya29.xxx...",
    "expiresIn": 3600,
    "projectId": "enikki-cloud",
    "region": "us-central1"
  }
  ```
