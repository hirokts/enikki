# 絵日記生成の非同期化

## Summary
現在の POST /diaries は同期実行で、画像生成に時間がかかるとレスポンスが遅延する。
バックグラウンドタスクとして非同期実行するよう改善する。

## Tasks

### バックグラウンド実行
- [ ] FastAPI の BackgroundTasks を使用
- [ ] または Cloud Tasks / Pub/Sub を検討
- [ ] POST /diaries は即座に `status: pending` を返す

### ステータス確認 API
- [ ] GET /diaries/{id} でステータス確認
- [ ] ポーリング or WebSocket でフロントエンドに通知

### エラーハンドリング
- [ ] バックグラウンド処理のエラーを Firestore に記録
- [ ] `status: failed` と `errorMessage` を保存

## Notes
- `implement_diary_generation_logic` の後続タスク
- 画像生成が 5-10 秒かかるため、UX 改善に必要
