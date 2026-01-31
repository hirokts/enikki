ADC（Application Default Credentials）を利用したキーレス(サービスアカウントの認証情報json)の実装したい

```.py
# ライブラリが勝手に環境変数(ADC)を見て認証を済ませてくれる
from google.cloud import aiplatform

aiplatform.init(project="your-project-id")
# Live APIの設定へ...
```

JSONキー方式は、ファイルを紛失・誤配・Git公開するリスクがあるので、最近は推奨されていない

理想のゴール

- 本番デプロイ（将来）: Cloud RunやCompute Engineにデプロイする際、JSONファイルを持ち運ぶ必要はありません。 環境変数も不要です。VMやコンテナに適切なIAM権限を付与するだけで、ADCが自動的に「あ、今はGoogle Cloudの内部にいるから、メタデータサーバーから権限を借りよう」と判断してくれます。
- ローカル開発環境、gcloud auth 方式

1. ホストマシン（Mac/Windows）でログイン
   まず、コンテナを立ち上げる前にホストのターミナルで実行します。

```.sh
gcloud auth application-default login
```

```.yaml
# docker-compose.yml
services:
  backend:
    image: my-vertex-ai-app
    volumes:
      # ホストのADC情報をコンテナ内にマウント
      - ~/.config/gcloud:/tmp/gcloud-config
    environment:,
      # ADCがマウントされたファイルを見に行くように指示
      - GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcloud-config/application_default_credentials.json
```
