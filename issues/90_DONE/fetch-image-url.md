# Fetch and Display Generated Diary Image

## Summary

生成された絵日記（画像と文章）をフロントエンドで表示するための処理を実装します。
バックエンドでの生成処理は非同期で行われるため、Firestore のステータス変更を監視し、完了後に画像URL (`imageUrl`) とテキスト (`diaryText`) を取得して表示する必要があります。

## Tasks

- [x] **Firestore 購読処理の実装**
  - [x] `id` を指定して Firestore の `diaries` ドキュメントをリアルタイム購読 (onSnapshot) する
  - [x] ステータス (`pending`, `processing`, `completed`, `failed`) に応じたUI制御

- [x] **UI実装**
  - [x] **Loading/Processing**: 「日記を書いています...」「絵を描いています...」などの待機画面
  - [x] **Completed**: 絵日記画像の表示 (`imageUrl`) と日記本文 (`diaryText`) の表示
  - [x] **Failed**: エラーメッセージの表示と再試行ボタン（必要であれば）

- [x] **画像アクセスの確認**
  - [x] 生成された GCS の URL がフロントエンドからアクセス可能か検証する
  - [x] 必要に応じて GCS バケットの公開設定 (`allUsers` への `Storage Object Viewer` 付与) または署名付きURLの発行を検討

## Notes

- **コンポーネント責務の変更**:
  - `MultimodalRecorder.svelte`: 会話終了後、バックエンドにデータを送信し、返却された `diaryId` を親コンポーネント (`+page.svelte`) に渡す (`oncomplete` イベントの引数を変更)。
  - `+page.svelte`: `diaryId` を受け取り、Firestore の `onSnapshot` で監視を開始する。ステータスに応じてローディング表示や完了表示を行う。

- **バックエンド (`process_diary_in_background`)**: 完了時に `imageUrl` と `diaryText` を Firestore に書き込みます。
- **GCS バケット**: 名前は `${PROJECT_ID}-enikki-images` (デフォルト)。
- **Firestore セキュリティルール**: 開発環境での検証を優先し、一時的に `diaries` コレクションの読み書きを許可する設定が必要になる可能性があります（現在はテストユーザー固定のため）。
- **画像URL**: バケットの権限設定によっては、公開URLへのアクセス詳細の確認が必要です。
