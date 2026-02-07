# discord_notification_on_diary_complete

## Summary
絵日記の生成が完了した際に、Discord Webhook を使用して通知を送信する。生成された画像と日記のテキストをDiscordチャンネルに投稿する。

## Tasks
- [x] Discord Webhook URL の環境変数を追加
- [x] Discord通知用のヘルパー関数を作成
- [x] `diary_workflow.py` の完了時に通知処理を追加
- [x] 通知内容のフォーマット（画像URL、日記テキスト、タイトルなど）
- [x] 動作確認

## Notes
- Discord Webhook は無料で簡単に設定可能
- Embed 形式で画像とテキストをリッチに表示できる
- 参考: https://discord.com/developers/docs/resources/webhook

### Discord Webhook の準備手順
1. Discordサーバーで通知を受け取りたいチャンネルを開く
2. チャンネル名の横にある ⚙️（歯車アイコン）をクリック
3. 「連携サービス」→「ウェブフック」を選択 → 「ウェブフックを作成」
4. 名前を設定（例: `Enikki Bot`）、アイコンも設定可能
5. 「ウェブフックURLをコピー」をクリック
6. URLを環境変数に設定:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxxx/yyyyy
   ```

### 実装について
- Webhookへの `POST` リクエストを送るだけ（追加ライブラリ不要、`httpx` でOK）
