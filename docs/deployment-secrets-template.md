# デプロイ用シークレット・コマンドメモ (テンプレート)

このファイルを `secrets/deployment-secrets.md` にコピーし、実際の値を記入して使用してください。
`secrets/` ディレクトリは `.gitignore` に含まれているため、Git にはコミットされません。

## プロジェクト設定
- **Project ID**: `YOUR_PROJECT_ID`
- **Region**: `asia-northeast1` (Cloud Run) / `us-central1` (Vertex AI)
- **Repo Name**: `enikki`
- **Bucket Name**: `YOUR_BUCKET_NAME`

## 1. サービスアカウント権限付与コマンド
```bash
PROJECT_ID="YOUR_PROJECT_ID"
PROJECT_NUMBER="YOUR_PROJECT_NUMBER"
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA" --role="roles/datastore.user"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA" --role="roles/storage.objectAdmin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA" --role="roles/aiplatform.user"
```

## 2. Cloud Run デプロイコマンド (初回/環境変数更新)
```bash
gcloud run deploy enikki-api \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --no-cpu-throttling \
  --set-env-vars "^@^GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID@GCP_REGION=us-central1@GCS_BUCKET_NAME=YOUR_BUCKET_NAME@FRONTEND_URL=https://YOUR_FRONTEND.web.app@ALLOWED_ORIGINS=https://YOUR_FRONTEND.web.app,http://localhost:5173@DISCORD_WEBHOOK_URL=YOUR_WEBHOOK_URL"
```

## 3. 環境変数更新のみ (Update Env Vars)
```bash
gcloud run services update enikki-api \
  --region asia-northeast1 \
  --update-env-vars "^@^ALLOWED_ORIGINS=https://YOUR_FRONTEND.web.app,http://localhost:5173@FRONTEND_URL=https://YOUR_FRONTEND.web.app"
```

## 4. Frontend 環境変数 (apps/web/.env.production)
本番環境のビルド時に必要な環境変数です。`apps/web/.env.production` を作成し設定してください。
```bash
VITE_API_URL=https://YOUR_BACKEND_API_URL.run.app
```

## 5. Firebase Hosting デプロイ (Frontend)
```bash
cd apps/web
pnpm build
firebase deploy --only hosting
```
