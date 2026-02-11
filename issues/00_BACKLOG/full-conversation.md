# LIVE API 会話全文の取得とバックエンド連携

## Summary

現在、フロントエンドからバックエンドに送信されるのは `report_diary_event` ツールの構造化引数のみ。
LIVE API の **transcription 機能**（`input_audio_transcription` / `output_audio_transcription`）を有効にし、
会話中に交わされたユーザーの発話・AIの応答をテキストとして蓄積。
日記生成ワークフローの入力として会話全文を活用することで、日記・画像の品質を向上させる。

### 現状のフロー

```
User ←(音声)→ Vertex AI Live API ←(audio/toolCall)→ LiveClient
                                                        ↓ toolCall
MultimodalRecorder → createDiary(構造化データのみ) → Backend → diary_workflow
```

### 目指すフロー

```
User ←(音声)→ Vertex AI Live API ←(audio/transcription/toolCall)→ LiveClient
                                    ↓ transcript 蓄積                ↓ toolCall
MultimodalRecorder → createDiary(構造化データ + 会話全文transcript) → Backend → diary_workflow
```

## Tasks

### Phase 1: フロントエンド — LiveClient に transcription を有効化

- [ ] `LiveClient.sendSetupMessage()` の setup config に以下を追加:
  ```json
  "input_audio_transcription": {},
  "output_audio_transcription": {}
  ```
  ※ `response_modalities` は `['AUDIO']` のまま変更しない
- [ ] `LiveClient` に transcript 蓄積用の配列を追加:
  ```typescript
  private transcript: TranscriptEntry[] = [];
  ```
- [ ] `handleMessage()` で `serverContent.inputTranscription` を検知し、ユーザー発話テキストを蓄積:
  ```typescript
  if (data.serverContent?.inputTranscription?.text) {
    this.transcript.push({
      role: "user",
      text: data.serverContent.inputTranscription.text,
      timestamp: Date.now(),
    });
    this.dispatchEvent(
      new CustomEvent("inputTranscription", {
        detail: data.serverContent.inputTranscription.text,
      }),
    );
  }
  ```
- [ ] `handleMessage()` で `serverContent.outputTranscription` を検知し、モデル応答テキストを蓄積:
  ```typescript
  if (data.serverContent?.outputTranscription?.text) {
    this.transcript.push({
      role: "model",
      text: data.serverContent.outputTranscription.text,
      timestamp: Date.now(),
    });
    this.dispatchEvent(
      new CustomEvent("outputTranscription", {
        detail: data.serverContent.outputTranscription.text,
      }),
    );
  }
  ```
- [ ] `getTranscript()` メソッドを公開:
  ```typescript
  getTranscript(): TranscriptEntry[] {
    return [...this.transcript];
  }
  ```
- [ ] `disconnect()` 時に transcript をクリアしないようにする（送信前に取得するため）

### Phase 2: フロントエンド — API 送信の拡張

- [ ] `api.ts` の `createDiary()` の引数型に `transcript` フィールドを追加:
  ```typescript
  transcript?: Array<{ role: 'user' | 'model'; text: string; timestamp: number }>;
  ```
- [ ] `MultimodalRecorder.svelte` の `toolCall` ハンドラーで `client.getTranscript()` を取得し `createDiary()` に渡す
- [ ] 「日記にする」ボタン（`endConversation`）からも transcript 付きで送信できるようにする

### Phase 3: バックエンド — transcript の受信と活用

- [ ] `models.py` の `ConversationLogRequest` に `transcript` フィールドを追加:
  ```python
  transcript: list[dict] | None = None
  ```
- [ ] `main.py` の `create_diary` で transcript を Firestore に保存し、ワークフローに渡す
- [ ] `diary_workflow.py` の `DiaryState` に `transcript` フィールドを追加
- [ ] `extract_keywords` ノードのプロンプトに transcript を組み込む
  - transcript がある場合は構造化データよりも transcript を優先的に使う
- [ ] `generate_diary` ノードのプロンプトに transcript を組み込む
  - 会話全文をもとに、よりリッチなキーワード抽出と日記文章生成を行う
- [ ] transcript が長すぎる場合の対策（トークン制限）

### Phase 4: 動作確認

- [ ] ローカル環境で会話 → 日記生成の E2E 動作確認
- [ ] transcript が正しく蓄積・送信・保存されていることを確認（コンソールログ）
- [ ] transcript ありの場合となしの場合で日記品質を比較

## Notes

### Live API transcription 機能の仕様（公式ドキュメントより）

**セットアップ**: setup config に空オブジェクトを指定するだけで有効化される

```json
{
  "setup": {
    "model": "...",
    "generation_config": {
      "response_modalities": ["AUDIO"]
    },
    "input_audio_transcription": {},
    "output_audio_transcription": {}
  }
}
```

**レスポンス形式**: `serverContent` 内の以下のフィールドで受信

- `serverContent.inputTranscription.text` — ユーザー音声入力の文字起こし
- `serverContent.outputTranscription.text` — モデル音声出力の文字起こし
- これらは `serverContent.modelTurn`（音声データ）と**並行して**送信される

**重要な制約**:

- `response_modalities` に `AUDIO` と `TEXT` を同時指定はできない（Config Error になる）
- transcription は `response_modalities` とは独立した機能で、`AUDIO` モードのまま利用可能
- transcription テキストは断片的に送られる可能性がある（蓄積して結合する必要あり）

### transcript のデータ構造

```typescript
type TranscriptEntry = {
  role: "user" | "model";
  text: string;
  timestamp: number; // Unix ms
};
```

### バックエンドの transcript 活用方針

- **extract_keywords**: transcript 全文からキーワードを抽出（構造化データの補完として）
- **generate_diary**: transcript を "原文" として渡し、会話の雰囲気・ニュアンスを反映した日記生成
- transcript が長い場合は要約してからプロンプトに入れる（トークン制限対策）
- transcript がない場合（旧API呼び出し、フォールバック等）は現行の構造化データのみで動作

### 参考ドキュメント

- [Live API capabilities guide - Audio transcriptions](https://ai.google.dev/gemini-api/docs/live-guide#audio-transcriptions)
- [Live API Limitations - Response modalities](https://ai.google.dev/gemini-api/docs/live-guide#response-modalities)
- [Vertex AI Live API WebSocket](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api/get-started-websocket?hl=ja)

### 変更対象ファイル

| ファイル                                                | 変更内容                                            |
| ------------------------------------------------------- | --------------------------------------------------- |
| `apps/web/src/lib/live-client.ts`                       | transcription 有効化、transcript 蓄積、イベント発火 |
| `apps/web/src/lib/api.ts`                               | `createDiary()` に transcript パラメータ追加        |
| `apps/web/src/lib/components/MultimodalRecorder.svelte` | transcript を取得して API に渡す                    |
| `apps/api/src/models.py`                                | `ConversationLogRequest` に transcript 追加         |
| `apps/api/src/main.py`                                  | transcript を Firestore 保存・ワークフローに伝播    |
| `apps/api/src/diary_workflow.py`                        | プロンプトに transcript を組み込み                  |
