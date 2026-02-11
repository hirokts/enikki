# LIVE API 設定のアップデート

## Summary

現在使用しているモデル `gemini-live-2.5-flash-preview-native-audio-09-2025` の設定を
[公式ドキュメント](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api?hl=ja) に基づいて最新のベストプラクティスに更新する。

## Tasks

### アフェクティブ ダイアログの有効化

- [x] setup config に `enable_affective_dialog: true` を追加
  - モデルがユーザーの感情表現（トーン）を理解して応答できるようになる

### 音声設定の最適化

- [x] `speech_config` に `language_code: "ja-JP"` を明示的に指定
- [x] 音声は現行の `Aoede` を維持（後で別音声を試す場合は変更可能）

### 音声アクティビティ検出 (VAD) の調整

- [x] `automatic_activity_detection` を追加:
  - `start_of_speech_sensitivity: LOW` — 環境音でトリガーしないように
  - `end_of_speech_sensitivity: LOW` — 日本語のフィラー（「えーと」「あのー」）で切れないように
  - `prefix_padding_ms: 200` — 冒頭 200ms のパディングで音声取りこぼしを防止

### プロアクティブ音声

- [x] 検討の結果、**無効のまま**とした
  - インタビュー形式ではユーザー発話に常に応答すべきため、プロアクティブ音声は不適

### モデルバージョンの確認

- [x] `gemini-live-2.5-flash-preview-native-audio-09-2025` は最新の安定版。現状維持

## Notes

### 適用した設定変更

```typescript
// Before
generation_config: {
  response_modalities: ['AUDIO'],
  speech_config: {
    voice_config: {
      prebuilt_voice_config: { voice_name: 'Aoede' }
    }
  }
}

// After
generation_config: {
  response_modalities: ['AUDIO'],
  speech_config: {
    voice_config: {
      prebuilt_voice_config: { voice_name: 'Aoede' }
    },
    language_code: 'ja-JP'
  }
},
enable_affective_dialog: true,
automatic_activity_detection: {
  start_of_speech_sensitivity: 'START_OF_SPEECH_SENSITIVITY_LOW',
  end_of_speech_sensitivity: 'END_OF_SPEECH_SENSITIVITY_LOW',
  prefix_padding_ms: 200
}
```

### 参考ドキュメント

- [Gemini 2.5 Flash Live API ネイティブ音声](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api?hl=ja)
- [Gemini の機能を構成する](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/configure-gemini-capabilities?hl=ja)
- [言語と音声を構成する](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/configure-language-voice?hl=ja)

### 変更対象ファイル

| ファイル                          | 変更内容                                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------------------------- |
| `apps/web/src/lib/live-client.ts` | setup config に `language_code`, `enable_affective_dialog`, `automatic_activity_detection` を追加 |
