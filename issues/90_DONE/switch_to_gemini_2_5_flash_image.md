# 画像生成モデルを Gemini 2.5 Flash Image (Nano Banana) に変更

## Summary
Imagen 3 (`imagen-3.0-generate-002`) から、Gemini ファミリーの画像生成モデル（通称 Nano Banana, Gemini 2.5 Flash Image）への移行を実施。
Gemini エコシステムへの統一と、将来的なマルチモーダル編集機能への布石。

## Tasks

### 調査
- [x] Vertex AI で利用可能な Gemini の画像生成モデルを確認する
    - `gemini-2.5-flash-image` モデルが利用可能
    - `google-genai` SDK を使用（`vertexai` SDK ではなく）
    - `us-central1` リージョンで利用可能

### 実装変更 (`src/diary_workflow.py`)
- [x] `ImageGenerationModel` (Imagen) から `google-genai` SDK への切り替え
    - `client.models.generate_content()` メソッドを使用
    - `response_modalities=["IMAGE"]` で画像生成を指定
- [x] プロンプトの調整
    - 既存プロンプトをそのまま使用可能

### 動作確認
- [x] 画像が正常に生成されるか確認
- [x] Cloud Storage へのアップロード確認

## Notes
- "Nano Banana" は Gemini 2.5 Flash Image のコードネーム
- `google-genai` パッケージを追加 (`uv add google-genai`)
- `pillow` パッケージを追加
- リージョンは `us-central1` を使用（新モデル対応のため）
- 参考ドキュメント: https://github.com/googleapis/python-genai
