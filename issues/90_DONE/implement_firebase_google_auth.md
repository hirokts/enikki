# implement_firebase_google_auth

## Summary
Firebase Authentication を使用した Google ログインを導入し、API Key による簡易認証からセキュアな認証フローへ移行します。
利用制限のためではなく、有効な Google アカウント保持者であることを確認するために使用します。

## Tasks
- [x] Firebase Web コンソールでの Google Auth 有効化（ユーザー作業）
- [x] フロントエンド: `firebase.ts` の環境変数設定（API Keyなど）
- [x] フロントエンド: Google ログインの実装
- [x] フロントエンド: 取得した ID トークンを `X-Firebase-Token` ヘッダーに乗せて送信するよう `api.ts` を修正
- [x] バックエンド: `firebase-admin` の導入
- [x] バックエンド: `verify_api_key` を `verify_firebase_token` に変更し、トークン検証ロジックを実装
- [x] バックエンド・フロントエンド: Firestore 接続情報の共有方法の整理
- [x] Firestore セキュリティルールの更新（必要に応じて）

## Notes
- `localStorage.setItem("apiKey", ...)` による手動設定を廃止する。
- バックエンドの環境変数 `API_KEY` を廃止し、Firebase サービスアカウント等の認証情報を使用する。
