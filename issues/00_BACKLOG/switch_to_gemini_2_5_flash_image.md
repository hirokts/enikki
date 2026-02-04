# 画像生成モデルを Gemini 2.5 Flash Image (Nano Banana) に変更

## Summary
現在使用している Imagen 3 (`imagen-3.0-generate-002`) から、Gemini ファミリーの画像生成モデル（通称 Nano Banana, Gemini 2.5 Flash Image）への移行を検討・実施する。
Gemini エコシステムへの統一と、将来的なマルチモーダル編集機能への布石とする。

## Tasks

### 調査
- [ ] Vertex AI で利用可能な Gemini の画像生成モデルを確認する
    - おそらく `gemini-2.0-flash` 系のモデルで画像生成機能が有効になっているか確認
    - 正式なモデルIDを特定する（例: `gemini-2.0-flash-exp` なのか、専用のエンドポイントがあるのか）

### 実装変更 (`src/diary_workflow.py`)
- [ ] `ImageGenerationModel` (Imagen) から `GenerativeModel` (Gemini) への切り替え
    - Gemini の画像生成 API の仕様に合わせてコードを修正
- [ ] プロンプトの調整
    - Gemini に適した指示方法への変更

### 動作確認
- [ ] 画像が正常に生成されるか確認
- [ ] 画風や品質のチェック
- [ ] 生成速度の確認

## Notes
- "Nano Banana" は Gemini 2.5 Flash Image のコードネーム
- 現状 Imagen 3 で安定しているため、移行によるメリット（速度、編集機能など）と比較して判断する
