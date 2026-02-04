# 絵日記生成の非同期化

## Summary
現在の POST /diaries は同期実行で、画像生成に時間がかかるとレスポンスが遅延する。
バックグラウンドタスクとして非同期実行するよう改善する。

## Tasks

### バックグラウンド実行
- [x] FastAPI の BackgroundTasks を使用
- [x] POST /diaries は即座に `status: pending` を返す
- [x] フロントエンドは Firestore リアルタイムリスナーでステータス監視（GET API 不要）

### エラーハンドリング
- [x] バックグラウンド処理のエラーを Firestore に記録
- [x] `status: failed` と `errorMessage` を保存

## Notes
- `implement_diary_generation_logic` の後続タスク
- 画像生成が 5-10 秒かかるため、UX 改善に必要
- **実装方針**:
  - FastAPI の `BackgroundTasks` を使用（Cloud Tasks / Pub/Sub は使わない）
  - POST /diaries は即座に `{ id, status: "pending" }` を返す
  - フロントエンドは Firestore リアルタイムリスナーでステータス変更を監視
  - エラー時は `status: failed` と `error` メッセージを Firestore に保存
