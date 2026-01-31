# connect_gemini_live_api

## Summary
フロントエンドから Vertex AI Multimodal Live API に接続し、Gemini と音声会話できるようにする。
バックエンドで取得したアクセストークンを使用して、WebSocket 経由でリアルタイム通信を行う。

## Tasks
### 接続基盤
- [x] Multimodal Live API への WebSocket 接続を実装
    - バックエンド `/auth/token` からトークンを取得
    - Vertex AI エンドポイントに接続
    - 接続状態の管理（接続中、切断、エラー）

### マイク入力
- [x] ブラウザでマイクを起動（`getUserMedia`）
- [x] 音声データを適切なフォーマットで Gemini に送信
- [x] 録音開始/停止の UI 実装

### Gemini からの応答
- [x] 音声レスポンスの受信と再生
- [x] テキストレスポンスの表示（デバッグ用）

### 動作確認
- [x] ローカル環境で Gemini と会話できることを確認
- [x] 会話ログの取得（後続の絵日記生成に使用）

## Notes
- **参考**: kickoff.md L354-360
- Multimodal Live API ドキュメント: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal-live/overview
- 既存の `MultimodalRecorder.svelte` コンポーネントを拡張する形で実装
- 会話終了後のバックエンドへのデータ送信は別issueで対応
- **接続方式について**:
    - **WebSocket (WSS)**: Gemini Live API のメイン接続方式。双方向リアルタイム通信。今回はこちらを使用。
    - **WebRTC**: Daily, LiveKit, Twilio 等のパートナー経由で利用可能（より高品質な音声/動画向け）
