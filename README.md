# 📔 Enikki (絵日記)

AIがあなたの1日をインタビューし、素敵な絵日記を生成するアプリケーションです。

## 🏗️ アーキテクチャ

- **Frontend**: SvelteKit (Tailwind CSS, Firebase SDK)
- **Backend**: FastAPI (Python, LangGraph)
- **AI**: Gemini 2.0 Flash (Multimodal Live API), Gemini 2.5 Flash (Text/Image generation)
- **Infrastructure**: Google Cloud (Cloud Run, Firestore, Cloud Storage, Artifact Registry)

---

## 💻 ローカル開発環境のセットアップ

### 前提条件
- Docker / Docker Compose
- Google Cloud CLI (gcloud)
- 有効な Google Cloud プロジェクトと Vertex AI API の有効化

### 手順

1. **Google Cloud 認証**
   ```bash
   gcloud auth application-default login
   ```

2. **環境変数の設定**
   `apps/api/.env` を `.env.example` を参考に作成します。

3. **アプリケーションの起動**
   ```bash
   docker compose up --build
   ```
   - API: `http://localhost:8000`
   - Web: `http://localhost:5173`

---

## 🚀 デプロイ手順 (Google Cloud)

### ⚙️ バックエンド (Cloud Run)

1. **Artifact Registry リポジトリの作成** (初回のみ)
   ```bash
   gcloud artifacts repositories create enikki --repository-format=docker --location=asia-northeast1
   ```

2. **Cloud Run へのデプロイ**
   `apps/api` ディレクトリで以下のコマンドを実行します。
   ```bash
   gcloud run deploy enikki-api \
     --source . \
     --region asia-northeast1 \
     --allow-unauthenticated \
     --set-env-vars "\
   GCP_PROJECT_ID=your-project-id,\
   GCP_REGION=us-central1,\
   GCS_BUCKET_NAME=your-bucket-name,\
   FRONTEND_URL=https://your-frontend.web.app,\
   ALLOWED_ORIGINS=https://your-frontend.web.app,\
   API_KEY=your-api-key,\
   DISCORD_WEBHOOK_URL=your-webhook-url"
   ```

3. **サービスアカウントへの権限付与**
   Cloud Run のサービスアカウント（デフォルトは `{プロジェクト番号}-compute@developer.gserviceaccount.com`）に以下のロールを付与する必要があります。
   - `roles/datastore.user` (Firestore 用)
   - `roles/storage.objectAdmin` (Cloud Storage 用)
   - `roles/aiplatform.user` (Vertex AI 用)

### 🌐 フロントエンド (Firebase Hosting)

1. **環境変数の設定**
   `apps/web/.env` に Cloud Run の URL を設定します。
   ```
   VITE_API_URL=https://enikki-api-xxxxx-an.a.run.app
   ```

2. **ビルドとデプロイ**
   ```bash
   cd apps/web
   pnpm install
   pnpm build
   firebase deploy --only hosting
   ```
