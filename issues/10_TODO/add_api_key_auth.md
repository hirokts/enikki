# add_api_key_auth

## Summary
`POST /auth/token` エンドポイントに API Key 認証を追加する。
フロントエンドは API Key を localStorage に保存し、リクエスト時に `X-API-Key` ヘッダーで送信する。

## Tasks
### バックエンド
- [ ] 環境変数 `API_KEY` を `.env` に追加
- [ ] `X-API-Key` ヘッダーを検証するミドルウェア/依存関係を実装
- [ ] 認証失敗時は `401 Unauthorized` を返却

### フロントエンド
- [ ] API Key 入力フォームを作成（初回のみ表示）
- [ ] localStorage に API Key を保存
- [ ] API リクエスト時に `X-API-Key` ヘッダーを付与

## Notes
- **セキュリティ**: ハッカソン/開発用途向け。本番では Firebase Auth 等を推奨。
- API Key はユーザーに事前に共有しておく想定
