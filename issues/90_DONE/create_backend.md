# create_backend

## Summary
`apps/api` に Python (FastAPI) のバックエンドプロジェクトをセットアップする。
今回は基本的なプロジェクト構造の作成とライブラリのインストールまでをスコープとし、具体的なロジック（認証や絵日記生成）の実装は別タスクとする。

## Tasks
- [x] `apps/api` の uv プロジェクト設定・依存関係追加
    - `fastapi`, `uvicorn`
    - `google-cloud-aiplatform`, `google-cloud-firestore`, `pydantic`
- [x] 基本的な FastAPI アプリケーション構造の作成 (`apps/api/src/main.py`)
    - ヘルスチェック用エンドポイント (`GET /`)
    - JSONレスポンスが返ることを確認
- [x] Docker Compose でバックエンドを起動できるようにする
    - `docker-compose.yml` の作成
    - `Dockerfile` の作成 (uv ベース)
- [x] 環境変数の管理
    - `.env.example` の作成（サンプル値を記載）
    - `.env` の作成（`.gitignore` に追加済みであることを確認）
- [x] ローカル開発環境の整備
    - 起動コマンドの確認 (`docker compose up` または `uv run uvicorn ...`)
    - README に手順を記載
- [x] 生成済みの絵日記を返すStubエンドポイントを用意

## Notes
- **重要**: 今回のスコープはプロジェクトのセットアップ（Hello World + Docker + Env）まで。
- フロントエンド -> Vertex AI 直結構成の下準備。
- 次のステップで Auth や Summary 機能を実装する。
- 環境変数の例:
    - `GCP_PROJECT_ID`: Google Cloud プロジェクトID
    - `GOOGLE_APPLICATION_CREDENTIALS`: サービスアカウントキーのパス（ローカル開発用）
