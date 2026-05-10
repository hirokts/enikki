# GCP / Firebase リソースの停止（ハッカソン終了後の課金対策）

## Summary
ハッカソン終了につき、課金が発生しないよう GCP / Firebase 上のリソースを停止・削除する。

## 確認済みリソース

| リソース | 実際の値 | 課金リスク |
|---|---|---|
| Cloud Run | `enikki-api` (asia-northeast1) | ⚠️ リクエスト数・CPU時間で課金 |
| Cloud Storage | `enikki-cloud-enikki-images` | ⚠️ ストレージ容量で課金 |
| Artifact Registry | `enikki` (asia-northeast1) | ⚠️ ストレージ容量で課金 |
| Firebase Hosting | `enikki-cloud.web.app` | 無料枠内なら無課金 |
| Firestore | `enikki-cloud` | 無料枠内なら無課金 |
| Firebase Auth | `enikki-cloud` | 無料枠内なら無課金 |
| Vertex AI | Gemini API | リクエスト時のみ課金（Cloud Run停止で解決） |

## Tasks

### 最優先（課金停止）
- [x] Cloud Run サービスを削除する
  ```bash
  gcloud run services delete enikki-api --region asia-northeast1 --project enikki-cloud --quiet
  ```
- [x] Cloud Storage バケットの中身を削除する
  ```bash
  gcloud storage rm -r gs://enikki-cloud-enikki-images
  ```
- [x] Artifact Registry のリポジトリを削除する
  ```bash
  gcloud artifacts repositories delete enikki --location asia-northeast1 --project enikki-cloud --quiet
  ```

### 任意（完全クリーンアップしたい場合）
- [ ] Firebase Hosting を無効化
  ```bash
  firebase hosting:disable --project enikki-cloud
  ```
- [ ] Firestore のデータを削除
- [ ] Firebase Authentication のユーザーを削除
- [x] GCP プロジェクトごと削除（全リソース一括・最も確実・30日間復元可能）
  ```bash
  gcloud projects delete enikki-cloud
  ```

## 実施記録

### 2026-05-10
- `gcloud run services delete enikki-api --region asia-northeast1 --project enikki-cloud --quiet` を実行し、Cloud Run サービスを削除
- `gcloud storage rm -r gs://enikki-cloud-enikki-images` を実行し、Cloud Storage バケットを削除
- `gcloud artifacts repositories delete enikki --location asia-northeast1 --project enikki-cloud --quiet` を実行し、Artifact Registry を削除
- `gcloud projects delete enikki-cloud` を実行し、GCP プロジェクトごと全削除（Firebase Hosting / Auth / Firestore も含む）
- プロジェクト削除から30日以内は `gcloud projects undelete enikki-cloud` で復元可能

## Notes
- **プロジェクト削除が一番確実**。30日間は復元可能なので、将来再開したい場合でも安心。
- Cloud Run の `--no-cpu-throttling` を有効にしていたため、放置すると課金が大きかった可能性あり。
- Vertex AI は呼び出し時のみ課金なので、Cloud Run を止めれば自動的に止まる。
- Discord Webhook URL は `secrets/deployment-secrets.md` に記録済みなので再構築時も参照可能。
