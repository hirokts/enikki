# add_api_key_auth

## Summary
`POST /auth/token` エンドポイントに API Key 認証を追加する。
フロントエンドは API Key を localStorage に保存し、リクエスト時に `X-API-Key` ヘッダーで送信する。

## Tasks
### バックエンド
- [x] 環境変数 `API_KEY` を `.env` に追加
- [x] `X-API-Key` ヘッダーを検証するロジックを実装
- [x] 認証失敗時は `401 Unauthorized` を返却

### フロントエンド
- [x] API呼び出しユーティリティ作成 (`$lib/api.ts`)
- [x] localStorage から API Key を取得して `X-API-Key` ヘッダーに付与
- [x] ページ読み込み時に自動で認証チェック＆console.log出力
- [-] ~~API Key 入力フォームを作成~~ → 手動で `localStorage.setItem()` を使用

## Notes
- **セキュリティ**: ハッカソン/開発用途向け。本番では Firebase Auth 等を推奨。
- API Key はユーザーに事前に共有しておく想定
- 設定方法: `localStorage.setItem('apiKey', 'my-api-key-name')`
