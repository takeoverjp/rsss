# RSS Summarizer

RSSで配信されている記事を、OpenAI APIを使って日本語に要約し、LINEに通知するツール。

## 実行方法

0. OpenAI API keyと、LINE Notify APIのaccess tokenを取得する

1. 0.で取得したkeyを使って、下記のコマンドを実行する

```
docker build --tag rsss-image .
docker run --rm -e OPENAI_API_KEY=xxx -e LINE_NOTIFY_ACCESS_TOKEN=xxx rsss-image python rsss.py
```

## AWS lambdaで実行する方法

1. 下記手順でdeploy用のAWS Lambda packageを生成する

```
docker build --tag rsss-image .
# docker run --rm rsss-image /build-lambda-package.sh
docker run --name lambda-pkg-build rsss-image bash -c "pip install -r requirements.txt -t ./package/ && cd /package && zip -r /lambda.zip ."
docker cp lambda-pkg-build:lambda.zip .
docker rm -v lambda-pkg-build
```

2. AWS Lambdaに以下の設定を行う

- ランタイムのハンドラを、`rsss.lambda_handler`にする
- 環境変数`OPENAI_API_KEY`と`LINE_NOTIFY_ACCESS_TOKEN`を設定する

2. AWS Lambdaに上記zipをdeployする
