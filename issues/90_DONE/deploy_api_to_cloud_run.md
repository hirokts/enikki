# deploy_api_to_cloud_run

## Summary
FastAPI バックエンドを Cloud Run にデプロイする。既存の Dockerfile を使用し、環境変数は Secret Manager で管理する。

## Tasks
- [x] Artifact Registry にリポジトリを作成
- [x] Cloud Run サービスを作成・デプロイ（gcloud CLI）
- [x] 環境変数を設定（GCP_PROJECT_ID, GCP_REGION, GCS_BUCKET_NAME, API_KEY, DISCORD_WEBHOOK_URL, FRONTEND_URL, ALLOWED_ORIGINS）
- [x] Secret Manager で機密情報を管理（API_KEY, DISCORD_WEBHOOK_URL）※環境変数での初期稼働を確認
- [x] サービスアカウントに必要な権限を付与（Firestore, Cloud Storage, Vertex AI）
- [x] CORS 設定を本番URLに対応（環境変数化完了）
- [x] 動作確認（ヘルスチェック OK、フロントエンドからの通信 OK）

### デプロイ済みURL
**Service URL**: https://enikki-api-690196371357.asia-northeast1.run.app

## Notes

### 1. 前提条件
```bash
# プロジェクト確認
gcloud config get-value project
# => your-project-id

# 必要なAPIが有効か確認
gcloud services list --enabled --filter="name:run.googleapis.com OR name:artifactregistry.googleapis.com"
```

### 2. Artifact Registry リポジトリ作成（初回のみ）
```bash
gcloud artifacts repositories create enikki \
  --repository-format=docker \
  --location=asia-northeast1 \
  --description="Enikki container images"
```

### 3. Cloud Run デプロイ（シンプル版）
```bash
cd apps/api

gcloud run deploy enikki-api \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars "\
GCP_PROJECT_ID=your-project-id,\
GCP_REGION=asia-northeast1,\
GCS_BUCKET_NAME=your-project-id-enikki-images,\
FRONTEND_URL=https://your-frontend-url.web.app,\
ALLOWED_ORIGINS=https://your-frontend-url.web.app,\
API_KEY=your-api-key,\
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/yyy"
```

### 4. Secret Manager を使う場合（推奨）
```bash
# シークレット作成
echo -n "your-api-key" | gcloud secrets create API_KEY --data-file=-
echo -n "https://discord.com/api/webhooks/xxx/yyy" | gcloud secrets create DISCORD_WEBHOOK_URL --data-file=-

# Cloud Run サービスアカウントにシークレットへのアクセス権を付与
gcloud secrets add-iam-policy-binding API_KEY \
  --member="serviceAccount:your-project-number-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding DISCORD_WEBHOOK_URL \
  --member="serviceAccount:your-project-number-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# シークレットを使ってデプロイ
gcloud run deploy enikki-api \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=your-project-id,GCP_REGION=asia-northeast1,..." \
  --set-secrets "API_KEY=API_KEY:latest,DISCORD_WEBHOOK_URL=DISCORD_WEBHOOK_URL:latest"
```

### 5. サービスアカウント権限
Cloud Run のデフォルトサービスアカウントに以下の権限が必要：
- `roles/datastore.user` - Firestore 読み書き
- `roles/storage.objectAdmin` - Cloud Storage 読み書き
- `roles/aiplatform.user` - Vertex AI 使用

```bash
# 権限付与例
PROJECT_ID=your-project-id
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/aiplatform.user"
```

### 6. デプロイ後の確認
```bash
# サービスURL取得
gcloud run services describe enikki-api --region asia-northeast1 --format='value(status.url)'

# ヘルスチェック
curl https://enikki-api-xxxxx-an.a.run.app/health
```

### 環境変数一覧
| 変数名 | 説明 | 機密性 |
|--------|------|--------|
| `GCP_PROJECT_ID` | GCPプロジェクトID | 低 |
| `GCP_REGION` | リージョン（asia-northeast1） | 低 |
| `GCS_BUCKET_NAME` | 画像保存バケット名 | 低 |
| `FRONTEND_URL` | フロントエンドURL（Discord通知用） | 低 |
| `ALLOWED_ORIGINS` | CORS許可オリジン（カンマ区切り） | 低 |
| `API_KEY` | API認証キー | **高** |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | **高** |
