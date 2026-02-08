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

詳細なセットアップ手順、環境変数の設定、トラブルシューティングについては、以下のドキュメントを参照してください。

👉 **[デプロイメントガイド (docs/deployment.md)](docs/deployment.md)**

### クイックコマンド (更新用)

**Frontend (Firebase Hosting)**
```bash
cd apps/web && pnpm build && firebase deploy --only hosting
```

**Backend (Cloud Run)**
```bash
cd apps/api && gcloud run deploy enikki-api --source . --region asia-northeast1 --allow-unauthenticated
```
