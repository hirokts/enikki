# Issue Management

Gitリポジトリ内でファイルベースで課題管理を行います。

## Workflow

1. **起票**: Makefile を使用して課題を作成します。
   ```bash
   make issue
   # プロンプトに従ってタイトル入力
   ```
   作成されたファイルは `issues/00_BACKLOG` に配置されます。

2. **着手**: タスクに着手する際は、ファイルを `20_DOING` に移動させてください。
   ```bash
   git mv issues/10_TODO/my-task.md issues/20_DOING/
   ```
3. **完了**: タスクが完了したら、ファイルを `90_DONE` に移動させてください。
   ```bash
   git mv issues/20_DOING/my-task.md issues/90_DONE/
   ```

## Directory Structure
- `00_BACKLOG`: アイデア、いつかやるタスク
- `10_TODO`: 次にやるべきタスク
- `20_DOING`: 現在進行中のタスク
- `90_DONE`: 完了したタスク
