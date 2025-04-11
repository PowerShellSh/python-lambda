import pytest
import boto3
import json
import structlog
import os
from app import lambda_handler
from botocore.client import BaseClient
from typing import Dict, Any, TYPE_CHECKING
from boto3.resources.base import ServiceResource

# LocalStackのエンドポイントを設定
endpoint_url = 'http://localstack:4566'

# structlogの設定
logger = structlog.get_logger()

@pytest.fixture
def s3_client() -> BaseClient:
    return boto3.client('s3', endpoint_url=endpoint_url)

@pytest.fixture
def dynamodb_client() -> ServiceResource:
    return boto3.resource(
        'dynamodb',
        endpoint_url=endpoint_url,
        region_name='us-east-1'
    )

@pytest.fixture
def aws_credentials() -> None:
    """LocalStack用のダミー認証情報"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'test'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
    os.environ['AWS_SECURITY_TOKEN'] = 'test'
    os.environ['AWS_SESSION_TOKEN'] = 'test'

def test_lambda_handler() -> None:
    # テストイベントの作成（EventModelの定義に合わせる）
    test_event = {
        'key': 'test-key',
        'bucket_name': 'test-bucket',
        'additional_data': {  # オプショナル
            'test': 'data'
        }
    }

    # Lambda関数の実行
    response: Dict[str, Any] = lambda_handler(test_event, None)

    # レスポンスの検証
    assert response['statusCode'] == 200
    
    # レスポンスのボディを検証（オプショナル）
    response_body = json.loads(response['body'])
    assert 'message' in response_body
    assert response_body['event']['key'] == 'test-key'
    assert response_body['event']['bucket_name'] == 'test-bucket'
    
    # ログの検証
    logger.info("test_completed", response=response)

def test_s3_operations(aws_credentials: None, s3_client: BaseClient) -> None:
    # バケットの作成
    bucket_name = 'test-bucket'
    s3_client.create_bucket(Bucket=bucket_name)
    logger.info("bucket_created", bucket_name=bucket_name)
    
    # オブジェクトのアップロード
    test_data = b'Hello, S3!'
    s3_client.put_object(Bucket=bucket_name, Key='test.txt', Body=test_data)
    logger.info("object_uploaded", bucket=bucket_name, key='test.txt')
    
    # オブジェクトの取得
    response = s3_client.get_object(Bucket=bucket_name, Key='test.txt')
    assert response['Body'].read() == test_data
    logger.info("object_retrieved", bucket=bucket_name, key='test.txt')

def test_dynamodb_operations(dynamodb_client: ServiceResource) -> None:
    table_name = 'test-table'
    
    # 既存のテーブルを削除（存在する場合）
    try:
        table = dynamodb_client.Table(table_name)
        table.delete()
        table.wait_until_not_exists()
    except dynamodb_client.meta.client.exceptions.ResourceNotFoundException:
        pass

    # テーブルの作成
    table = dynamodb_client.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    
    # テーブルが作成されるまで待機
    table.wait_until_exists()
    
    # アイテムの追加
    table.put_item(Item={'id': '1', 'name': 'test'})
    logger.info("item_added", table=table_name, id='1')
    
    # アイテムの取得
    response = table.get_item(Key={'id': '1'})
    assert response['Item']['name'] == 'test'
    logger.info("item_retrieved", table=table_name, id='1') 