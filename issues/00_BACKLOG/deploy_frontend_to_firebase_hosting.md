# deploy_frontend_to_firebase_hosting

## Summary
SvelteKit フロントエンドを Firebase Hosting にデプロイする。静的サイト生成（SSG）で出力し、SPAとして配信する。

## Tasks
- [ ] Firebase プロジェクトに Hosting を設定（firebase init hosting）
- [ ] 環境変数を設定（API_URL を本番の Cloud Run URL に）
- [ ] ビルド設定の確認（pnpm build）
- [ ] firebase.json の設定（rewrites, headers など）
- [ ] デプロイ（firebase deploy --only hosting）
- [ ] カスタムドメイン設定（オプション）
- [ ] 動作確認

## Notes
### セットアップコマンド
```bash
cd apps/web
firebase init hosting
# public: build
# SPA: yes
# overwrite: no

pnpm build
firebase deploy --only hosting
```

### 環境変数（フロントエンド）
- `PUBLIC_API_URL`: Cloud Run の本番URL（例: https://enikki-api-xxxxx-an.a.run.app）

### firebase.json 設定例
```json
{
  "hosting": {
    "public": "build",
    "rewrites": [{ "source": "**", "destination": "/200.html" }]
  }
}
```

