# create_deployment_doc

## Summary
README.md に記載されていたデプロイ手順を詳細化し、トラブルシューティングや運用ナレッジを含めた専用ドキュメント `docs/deployment.md` を作成する。これまでの試行錯誤（Cloud Run設定、環境変数、リージョン制限など）を形式知として残す。

## Tasks
- [x] `docs/deployment.md` ファイルの作成
- [x] 前提条件と初回セットアップ手順の記述（Backend/Frontend）
- [x] アプリケーション更新手順の記述
- [x] 環境変数・シークレット管理の記述（カンマのエスケープなど）
- [x] トラブルシューティング（CPU Throttling, Region, CORS）の追記
- [x] README.md からのリンク設定と内容の整理
- [x] `docs/deployment-secrets-template.md` の作成（秘密情報管理用）
- [x] `docs/deployment.md` にシークレット運用の記述を追加

## Notes
### ドキュメント構成案
1. **はじめに (Overview)**
   - アーキテクチャ概要
   - 本番環境URL
2. **前提条件 (Prerequisites)**
   - gcloud, Firebase CLI, Docker
3. **初回セットアップ手順 (First-time Setup)**
   - Backend: Artifact Registry, サービスアカウント権限, 初期デプロイ
   - Frontend: Firebase Project, 環境変数, ビルド・デプロイ
4. **更新手順 (Deployment Workflow)**
   - フロントエンド・バックエンドそれぞれの更新コマンド
5. **環境変数とシークレット管理**
   - 必要な変数一覧
   - カンマを含む値の設定方法（`^@^` デリミタ）
6. **運用・トラブルシューティング (Troubleshooting)**
   - 非同期処理停止問題（CPU Throttling）
   - Gemini APIリージョン問題
   - CORS設定
