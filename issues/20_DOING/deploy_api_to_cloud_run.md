# deploy_api_to_cloud_run

## Summary
FastAPI バックエンドを Cloud Run にデプロイする。既存の Dockerfile を使用し、環境変数は Secret Manager で管理する。

## Tasks
- [ ] Artifact Registry にリポジトリを作成
- [ ] Cloud Run サービスを作成・デプロイ（gcloud CLI）
- [ ] 環境変数を設定（GCP_PROJECT_ID, GCP_REGION, GCS_BUCKET_NAME, API_KEY, DISCORD_WEBHOOK_URL, FRONTEND_URL）
- [ ] Secret Manager で機密情報を管理（API_KEY, DISCORD_WEBHOOK_URL）
- [ ] サービスアカウントに必要な権限を付与（Firestore, Cloud Storage, Vertex AI）
- [ ] CORS 設定を本番URLに対応
- [ ] 動作確認

## Notes
### デプロイコマンド例
```bash
cd apps/api
gcloud run deploy enikki-api \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=enikki-cloud,GCP_REGION=asia-northeast1,..."
```

### 必要な権限
- Firestore User
- Storage Object Admin
- Vertex AI User

