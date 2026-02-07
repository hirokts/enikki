# Renew Design

## Summary

`sample/my-app` のデザインを参考に、`apps/web` のUIを刷新する。
現在のシンプルなデザインから、ノスタルジックで温かみのある「絵日記」らしいデザインに変更する。

### 方針

- **既存機能はそのまま維持** - レコーダー、日記表示等の機能は変更なし
- **デザインのみ適用** - カラー、フォント、スタイルを刷新
- **ダークモードは対象外**

### 変更のポイント

- **カラーパレット**: 現在のブルー/グレー系 → 温かみのあるブラウン/アンバー系
- **フォント**: Zen Maru Gothic（丸ゴシック）+ DotGothic16（ピクセルフォント）
- **雰囲気**: 懐かしい日本の絵日記・冬の日々をイメージ

## Tasks

### Phase 1: デザインシステムの導入

- [ ] Google Fonts の設定（Zen Maru Gothic, DotGothic16）
- [ ] `app.css` にカラー変数を追加（oklch形式）
  - Primary: `oklch(0.45 0.12 30)` - 深い茶色/赤褐色
  - Accent: `oklch(0.75 0.15 55)` - 暖かいオレンジ/アンバー
  - Background: `oklch(0.97 0.01 85)` - 温かみのあるオフホワイト
  - その他 muted, border, card 等
- [ ] アニメーション定義の追加（snow animation 等）

### Phase 2: レイアウト・ナビゲーションの刷新

- [ ] `+layout.svelte` をリニューアル
  - ロゴの「絵」部分をアクセントカラーで強調
  - スクロールに応じて背景が変化するヘッダー
  - フッターのスタイル更新

### Phase 3: メインページのデザイン適用

- [ ] `+page.svelte` にヒーロースタイルを適用
  - 背景画像（`static/images/winter-hero.jpg`）
  - グラデーションオーバーレイ
  - Snowアニメーション
  - 既存のレコーダー機能はそのまま維持
- [x] 背景画像の配置（`static/images/winter-hero.jpg`）

### Phase 4: 既存コンポーネントのスタイル更新

- [ ] `MultimodalRecorder.svelte` のスタイル更新
  - 新しいカラーパレットに合わせる
  - ボタンのスタイル調整
- [ ] `DiaryCard.svelte` のスタイル更新
  - カード背景、ボーダーを新デザインに
- [ ] 生成中・エラー画面のスタイル更新

### Phase 5: 仕上げ・動作確認

- [ ] レスポンシブ対応の確認（モバイル/タブレット/デスクトップ）
- [ ] アニメーションのパフォーマンス確認
- [ ] クロスブラウザ動作確認

## Notes

### 参照元ファイル（sample/my-app）

- `app/globals.css` - カラー変数、フォント、アニメーション定義
- `app/layout.tsx` - フォント読み込み、メタデータ
- `components/hero-section.tsx` - ヒーローセクション
- `components/navigation.tsx` - ナビゲーション

### 技術的な変換ポイント

| React (Next.js)    | Svelte (SvelteKit)                  |
| ------------------ | ----------------------------------- |
| `useState`         | `$state`                            |
| `useEffect`        | `onMount`                           |
| `className`        | `class`                             |
| JSX `{}`           | Svelte `{}`                         |
| `next/font/google` | `app.html` で Google Fonts 読み込み |

### カラーパレット詳細（oklch形式）

```css
/* Light mode */
--background: oklch(0.97 0.01 85);
--foreground: oklch(0.25 0.03 40);
--card: oklch(0.99 0.005 85);
--primary: oklch(0.45 0.12 30);
--primary-foreground: oklch(0.98 0.01 85);
--secondary: oklch(0.85 0.05 220);
--accent: oklch(0.75 0.15 55);
--muted: oklch(0.92 0.02 85);
--border: oklch(0.88 0.03 85);
```

### 対象ファイル

- `apps/web/src/app.css`
- `apps/web/src/app.html`
- `apps/web/src/routes/+layout.svelte`
- `apps/web/src/routes/+page.svelte`
- `apps/web/src/lib/components/MultimodalRecorder.svelte`
- `apps/web/src/lib/components/DiaryCard.svelte`
