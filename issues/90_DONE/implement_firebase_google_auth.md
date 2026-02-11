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
- `localStorage.setItem("apiKey", ...)` による手動設定を廃止した。
- バックエンドの環境変数 `API_KEY` を廃止し、Firebase ID トークンによる認証に統合。
- **Firebase コンソールでの操作**:
    - **Authentication 画面**: 「始める」をクリックし、Sign-in method で **Google** を有効化。
    - **アプリの登録**: プロジェクト設定から Web アプリ（マイアプリ）を追加登録し、`firebaseConfig`（API Key や App ID 等）を取得した。
- **トラブルシューティング**: 導入時に `CONFIGURATION_NOT_FOUND` エラーが発生したが、Google Cloud コンソールで Identity Toolkit API を有効化することで解決した。
- **リファクタリング**: 独自の環境変数 `GCP_PROJECT_ID` を廃止し、Google Cloud の標準である `GOOGLE_CLOUD_PROJECT` に統一した。これにより、Firebase Admin SDK や Vertex AI SDK との親和性が向上。
- **UI/UX**: ログイン後の画面からメールアドレスや生成中のドキュメント ID を削除し、よりクリーンな見た目に調整した。
- **デプロイ**: Cloud Run デプロイ時、Firebase トークン検証のために `GOOGLE_CLOUD_PROJECT` の明示的な設定が必要であることを確認済み。
