# 🚀 デプロイメントガイド

Enikki (絵日記) アプリケーションのデプロイ環境構築、更新手順、およびトラブルシューティングのドキュメントです。

## 1. はじめに (Overview)

### アーキテクチャ構成
- **Frontend**: Firebase Hosting (SvelteKit SSG/SPA)
- **Backend**: Cloud Run (FastAPI, Python)
- **Database**: Cloud Firestore
- **Storage**: Cloud Storage (for images)
- **AI**: Vertex AI (Gemini 2.5 Flash, Gemini 2.0 Flash)

### 本番環境 URL
- **Frontend**: `https://your-frontend.web.app`
- **Backend API**: `https://your-backend-api-url.run.app`

## 2. 前提条件 (Prerequisites)

以下のツールがインストールされ、認証済みであること。

- **Google Cloud CLI (gcloud)**
  - `gcloud auth login`
  - `gcloud config set project your-project-id`
- **Firebase CLI**
  - `npm install -g firebase-tools`
  - `firebase login`
- **Docker / Docker Compose** (ローカル開発用)

## 3. 初回セットアップ手順 (First-time Setup)

### 3.1 バックエンド (Cloud Run)

1. **Artifact Registry リポジトリ作成**
   ```bash
   gcloud artifacts repositories create enikki \
     --repository-format=docker \
     --location=asia-northeast1 \
     --description="Enikki container images"
   ```

2. **サービスアカウントへの権限付与**
   Cloud Run のデフォルトサービスアカウント (`{PROJECT_NUMBER}-compute@developer.gserviceaccount.com`) に以下のロールが必要です。
   - `roles/datastore.user` (Firestore アクセス)
   - `roles/storage.objectAdmin` (画像アップロード)
   - `roles/aiplatform.user` (Gemini API 使用)

   ```bash
   # 例: プロジェクト番号の取得
   PROJECT_NUMBER=$(gcloud projects describe your-project-id --format="value(projectNumber)")
   SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
   
   # 権限付与
   gcloud projects add-iam-policy-binding your-project-id --member="serviceAccount:$SA" --role="roles/datastore.user"
   gcloud projects add-iam-policy-binding your-project-id --member="serviceAccount:$SA" --role="roles/storage.objectAdmin"
   gcloud projects add-iam-policy-binding your-project-id --member="serviceAccount:$SA" --role="roles/aiplatform.user"
   ```

3. **初期デプロイ**
   `apps/api` ディレクトリで実行します。
   ```bash
   gcloud run deploy enikki-api \
     --source . \
     --region asia-northeast1 \
     --allow-unauthenticated \
     --set-env-vars "GCP_PROJECT_ID=your-project-id,GCP_REGION=us-central1,..."
   ```
   ※ `GCP_REGION` は Gemini API の制限により `us-central1` を推奨。
   ※ `ALLOWED_ORIGINS` にカンマが含まれる場合の注意点は「トラブルシューティング」を参照。

### 3.2 フロントエンド (Firebase Hosting)

1. **Firebase プロジェクト設定**
   `apps/web/.firebaserc` にプロジェクトIDを設定します。
   ```json
   { "projects": { "default": "your-project-id" } }
   ```

2. **環境変数の設定 (本番用)**
   `apps/web/.env.production` を作成し、Cloud Run の本番URLを設定します。
   ```bash
   VITE_API_URL=https://your-backend-api-url.run.app
   ```
   ※ `.env.production` は `.gitignore` に含まれます。

3. **ビルドとデプロイ**
   ```bash
   cd apps/web
   pnpm install
   pnpm build
   firebase deploy --only hosting
   ```
   ※ `pnpm build` は自動的に `.env.production` を読み込みます。

## 4. アプリケーション更新手順 (Update Workflow)

開発が進み、コードを変更した後の定常的なデプロイ手順です。

### 🌐 フロントエンドの更新
```bash
cd apps/web
pnpm build
firebase deploy --only hosting
```

### ⚙️ バックエンドの更新
環境変数は前回の設定が引き継がれるため、ソースコードの指定のみで更新可能です。
```bash
cd apps/api
gcloud run deploy enikki-api --source . --region asia-northeast1 --allow-unauthenticated
```

## 5. 環境変数とシークレット管理

### 必要な環境変数一覧 (Backend)
| 変数名 | 説明 | 設定例 |
|---|---|---|
| `GCP_PROJECT_ID` | プロジェクトID | `your-project-id` |
| `GCP_REGION` | 使用するリージョン (Gemini用) | `us-central1` |
| `GCS_BUCKET_NAME` | 画像保存バケット | `your-project-id-enikki-images` |
| `FRONTEND_URL` | フロントエンドURL (Discord通知用) | `https://your-frontend.web.app` |
| `ALLOWED_ORIGINS` | CORS許可オリジン (カンマ区切り) | `https://your-frontend.web.app,http://localhost:5173` |
| `API_KEY` | API認証キー | (Secret推奨) |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | (Secret推奨) |

### 環境変数の更新における注意点 (カンマのエスケープ)
`gcloud` コマンドで環境変数を更新する際、値にカンマが含まれる（例：`ALLOWED_ORIGINS`）とエラーになることがあります。
この場合、カスタムデリミタ（`^@^`など）を使用してください。

**例:**
```bash
gcloud run services update enikki-api \
  --region asia-northeast1 \
  --update-env-vars "^@^ALLOWED_ORIGINS=https://a.com,https://b.com@FRONTEND_URL=..."
```

### ローカルでのシークレット管理運用 (推奨)
プロジェクトIDやAPIキーなどの機密情報を含むデプロイコマンドを、Git管理外のローカルファイルで管理する方法を提供しています。

1. **テンプレートのコピー**
   ```bash
   mkdir -p secrets
   cp docs/deployment-secrets-template.md secrets/deployment-secrets.md
   ```
   ※ `secrets/` ディレクトリは `.gitignore` に含まれているため、Gitにはコミットされません。

2. **値の記入**
   `secrets/deployment-secrets.md` を開き、`YOUR_PROJECT_ID` や `YOUR_API_KEY` などのプレースホルダーを実際の値に書き換えてください。

3. **利用方法**
   デプロイや環境変数の更新時は、このファイルに記述したコマンドをターミナルにコピー＆ペーストして実行します。

## 6. 運用・トラブルシューティング (Troubleshooting)

### Q. バックグラウンド処理（日記生成）が途中で止まる、完了しない
**原因**: Cloud Run はデフォルトで、HTTPレスポンスを返すとCPU割り当てを停止（スロットリング）します。非同期処理 (`BackgroundTasks`) が完了する前にCPUが止まっている可能性があります。
**解決策**: `--no-cpu-throttling` フラグを有効にするか、コンソールで「CPUを常に割り当てる」設定に変更してください。
```bash
gcloud run services update enikki-api --region asia-northeast1 --no-cpu-throttling
```

### Q. Gemini API で "404 Not Found" や "Publisher Model not found" エラーが出る
**原因**: 使用しているモデル（Gemini 2.5 Flash / 2.0 Flash）が、Cloud Run のリージョン（asia-northeast1）で利用できない、または `asia-northeast1` のエンドポイントから `us-central1` のモデルを呼ぼうとして失敗している可能性があります。
**解決策**: 環境変数 `GCP_REGION` を `us-central1` に設定してください。
```bash
gcloud run services update enikki-api --region asia-northeast1 --update-env-vars GCP_REGION=us-central1
```

### Q. フロントエンドから API を叩くと CORS エラーになる
**原因**: `ALLOWED_ORIGINS` 環境変数にフロントエンドのオリジンが含まれていないか、設定時のカンマエスケープ漏れで正しく反映されていない可能性があります。
**解決策**: 「環境変数の更新における注意点」を参照し、正しいオリジンを設定してください。
