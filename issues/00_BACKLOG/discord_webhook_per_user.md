# Discord Webhook URLをユーザーごとの設定に変更

## Summary
現在、Discord Webhook URLはバックエンドの環境変数（`DISCORD_WEBHOOK_URL`）で一律設定されている。
これをユーザーごとに設定できるようにする。バックエンドには保存せず、フロントの localStorage で管理し、日記作成リクエスト時に一緒に送る方式にする。

## Tasks
- [ ] フロント: トップ画面に「🔔 通知設定」UIを追加（モーダル or インライン）
  - [ ] Discord Webhook URL の入力・保存・削除
  - [ ] localStorage での永続化
- [ ] フロント: `createDiary` で localStorage の webhook URL をリクエストボディに含める
- [ ] バックエンド: `ConversationLogRequest` に `discordWebhookUrl: str | None = None` を追加
- [ ] バックエンド: `DiaryState` に `discord_webhook_url` フィールドを追加し、ワークフローに引き渡す
- [ ] バックエンド: `discord_notifier.py` を環境変数ではなく引数で URL を受け取るように変更
- [ ] バックエンド: `process_diary_in_background` で webhook URL をワークフローに渡す
- [ ] バックエンド: 環境変数 `DISCORD_WEBHOOK_URL` の参照を削除
- [ ] 動作確認: webhook URL 設定あり → Discord に通知が届く
- [ ] 動作確認: webhook URL 設定なし → 通知はスキップされる

## Notes
- ハッカソン向けのシンプルな実装。バックエンドでの永続化は行わない
- Webhook URL はユーザーのブラウザ localStorage に保存される
- セキュリティ上、Webhook URL はリクエストごとにフロントから送信される（バックエンドはステートレス）
- 環境変数 `DISCORD_WEBHOOK_URL` は今後不要になる（Cloud Run のデプロイ設定からも除外可能）
