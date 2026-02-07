# add_favicon_to_frontend

## Summary
フロントエンドでfaviconが見つからないエラー（404）を解消するため、適切なfaviconを追加する。

## Tasks
- [x] faviconファイル（SVGまたはICO）を作成/準備
- [x] `apps/web/static/` にfaviconを配置
- [x] `app.html` でfaviconを参照するよう設定
- [x] ブラウザで動作確認

## Notes
- 日記帳と太陽をモチーフにしたSVGアイコンを元に作成
- SvelteKitでは`static/`ディレクトリにファイルを配置
- SVGからICOへの変換: `convert -background transparent favicon.svg -define icon:auto-resize=48,32,16 favicon.ico` (ImageMagick)
- favicon.icoのみを使用（SVGは不要）

