# Update Prompt - 会話全文収集

## Summary

Live API から収集する情報量が少なく、画像生成・日記テキスト生成の精度が低い問題を改善する。
**アプローチA: 会話全文（トランスクリプト）を収集** で実装する。

### 現状の問題

1. **情報量が少ない**: 現在のツールパラメータは基本的な情報（date, location, activity, feeling, summary, joke_hint）のみ
2. **画像生成の精度**: 情報が曖昧だと生成される画像もイメージ通りにならない
3. **日記テキストの品質**: ジョークや詳細が不足していると面白みに欠ける

### 解決策

会話の全文（トランスクリプト）をバックエンドに送信し、LLMで必要な情報を抽出する。

## Tasks

### Phase 1: フロントエンド - テキストモダリティの追加

- [x] `live-client.ts`: `response_modalities` に `TEXT` を追加

  ```typescript
  generation_config: {
    response_modalities: ['AUDIO', 'TEXT'],
    ...
  }
  ```

- [x] `live-client.ts`: テキストレスポンスをイベントで発火
  - `serverContent.modelTurn.parts` にテキストがある場合を処理
  - `text` イベントを発火

- [x] `MultimodalRecorder.svelte`: 会話履歴を蓄積
  ```typescript
  let conversationHistory: Array<{
    role: "user" | "ai";
    text: string;
    timestamp: string;
  }> = [];
  ```

### Phase 2: フロントエンド - 会話ターン数の制御

**要件:**

- 最低 **3回** の往復がないと終了できない
- **8回** を超えると自然に会話を終了して絵日記作成へ

- [x] `live-client.ts`: システムプロンプトにターン数ルールを追加

  ```
  ## 会話のターン数ルール
  1. 最低3往復は会話を続けてください。3回未満でreport_diary_eventを呼ばないでください。
  2. 8往復を超えたら、自然に会話をまとめて report_diary_event を呼び出してください。
     例: 「たくさんお話聞けました！素敵な一日だったね。じゃあ、絵日記を作るね！」
  ```

- [x] `MultimodalRecorder.svelte`: ターン数カウンター追加

  ```typescript
  let turnCount = $state(0); // ユーザー発話ごとにインクリメント
  ```

- [x] `MultimodalRecorder.svelte`: 終了ボタンの制御
  - 3ターン未満: 終了ボタン非表示または無効化
  - 3ターン以上: 終了ボタン有効
  - 8ターン超過後: 自動的にAIが終了（フロントエンドでの強制終了は不要）

### Phase 3: フロントエンド - ツールパラメータの更新

- [x] `live-client.ts`: `report_diary_event` に `conversation_transcript` を追加

  ```typescript
  conversation_transcript: {
    type: 'STRING',
    description: '会話の全文（JSON形式）。ユーザーとAIの全ての発話を含む。'
  }
  ```

- [x] 既存パラメータの扱い
  - 残す: `date`, `location`, `activity`, `feeling`, `joke_hint`
  - 削除: `summary`（全文から生成するため不要）

### Phase 4: バックエンド - モデル更新

- [x] `models.py`: `ConversationLogRequest` に `conversation_transcript` を追加

  ```python
  conversation_transcript: str  # JSON形式の会話全文
  ```

- [ ] `models.py`: 会話エントリーの型定義を追加（オプション）
  ```python
  class ConversationEntry(BaseModel):
      role: Literal['user', 'ai']
      text: str
      timestamp: str
  ```

### Phase 5: バックエンド - ワークフロー改善

- [x] `diary_workflow.py`: キーワード抽出で会話全文を活用
  - 入力: `conversation_transcript`

- [x] `diary_workflow.py`: 日記テキスト生成で会話全文を活用
  - 全文を参照してより詳細な日記を生成

- [ ] `diary_workflow.py`: 画像生成プロンプトの改善
  - 抽出された視覚的要素を活用
  - より具体的なシーン描写を生成

### Phase 6: テスト・検証

- [ ] 実際の会話で全文が正しく収集されることを確認
- [ ] バックエンドで情報抽出が正しく動作することを確認
- [ ] 生成される画像・テキストの品質向上を確認

## Notes

### 技術的な検討事項

#### 1. ユーザー発話のテキスト取得

Live API でユーザーの音声入力のテキスト（音声認識結果）が取得できるか確認が必要。

- 取得可能な場合: そのまま会話履歴に追加
- 取得不可の場合: AIの応答のみを蓄積するか、別途音声認識を行う

#### 2. 会話履歴のサイズ

長い会話だと `conversation_transcript` が大きくなる可能性。

- 制限: 最大○ターンまで、または最大○文字まで
- 圧縮: 古い発話は要約するなど

#### 3. エラーハンドリング

- 全文が空の場合のフォールバック
- パース失敗時の処理

### 実装順序の提案

```
1. live-client.ts の TEXT モダリティ追加（小さな変更） ✅
2. テキストイベントの発火を確認 ✅
3. 会話履歴の蓄積ロジック実装 ← 次のステップ
4. ツールパラメータ更新 ✅
5. バックエンドのモデル更新 ✅
6. ワークフローの情報抽出ノード追加 ✅
7. 画像/テキスト生成の改善 ✅
8. E2Eテスト
```

### 関連ファイル

**フロントエンド:**

- `apps/web/src/lib/live-client.ts` - Live API接続
- `apps/web/src/lib/components/MultimodalRecorder.svelte` - レコーダーUI
- `apps/web/src/lib/api.ts` - バックエンドAPI呼び出し

**バックエンド:**

- `apps/api/src/models.py` - データモデル
- `apps/api/src/main.py` - APIエンドポイント
- `apps/api/src/diary_workflow.py` - 日記生成ワークフロー
