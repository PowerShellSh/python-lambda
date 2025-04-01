# ローカル開発環境セットアップガイド

## 前提条件
- Docker と Docker Compose がインストールされていること
- AWS CLI がインストールされていること
- Python 3.12 以上がインストールされていること

## セットアップ手順

### 1. AWS CLIの設定
ローカルテスト用のAWS認証情報を設定します：
```bash
aws configure

# 以下の値を入力してください
AWS Access Key ID: test
AWS Secret Access Key: test
Default region name: ap-northeast-1
Default output format: json
```

### 2. Dockerコンテナの起動
プロジェクトのルートディレクトリで以下のコマンドを実行します：
```bash
# Dockerコンテナをビルドして起動
docker-compose up --build

# バックグラウンドで実行する場合
docker-compose up -d --build

# pytest環境にログインする
docker exec -it python-lambda-test-1 /bin/bash
pytest /tests -v # テスト実行
```

### 3. S3バケットの操作方法

#### バケットの一覧を表示
```bash
aws --endpoint-url=http://localhost:4566 s3 ls
```

#### 特定のバケットの中身を確認
```bash
aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket
```

#### ファイルをアップロードする
```bash
# テストファイルを作成
echo "Hello, LocalStack!" > test.txt

# ファイルをアップロード
aws --endpoint-url=http://localhost:4566 s3 cp test.txt s3://test-bucket/
```

#### バケット内のオブジェクト詳細を確認
```bash
aws --endpoint-url=http://localhost:4566 s3api list-objects --bucket test-bucket
```

### 4. コンテナの停止
```bash
# コンテナを停止
docker-compose down

# コンテナとボリュームを完全に削除する場合
docker-compose down -v
```

## トラブルシューティング

### エンドポイントに接続できない場合
- Dockerコンテナが正常に起動しているか確認してください：
```bash
docker-compose ps
```

### 認証エラーが発生する場合
- AWS CLIの認証情報が正しく設定されているか確認してください：
```bash
aws configure list
```

### バケットが見つからない場合
- テストコードが正常に実行され、バケットが作成されているか確認してください
- LocalStackのログを確認してください：
```bash
docker-compose logs localstack
```

## 開発環境の構成
- LocalStack: AWSサービスのローカルエミュレーション
  - S3
  - DynamoDB
  - Lambda
- Poetry: Python依存関係管理
- pytest: テストフレームワーク

## 参考リンク
- [LocalStack公式ドキュメント](https://docs.localstack.cloud/overview/)
- [AWS CLI公式ドキュメント](https://aws.amazon.com/cli/) 