import json
import boto3
import os
import structlog

# LocalStackのエンドポイントを設定
endpoint_url = 'http://localstack:4566'

# LocalStack用のAWSリージョンを設定
region_name = 'us-east-1'  # LocalStackのデフォルトリージョン

# structlogの設定
logger = structlog.get_logger()

# S3クライアントの初期化
s3 = boto3.client('s3', endpoint_url=endpoint_url, region_name=region_name)

# DynamoDBクライアントの初期化
dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url, region_name=region_name)

def lambda_handler(event, context):
    try:
        # リクエストのログ
        logger.info("lambda_request", event_data=event)
        
        # レスポンスの作成
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Hello from Lambda!',
                'event': event
            })
        }
        
        # レスポンスのログ
        logger.info("lambda_response", response=response)
        return response
        
    except Exception as e:
        # エラーのログ
        logger.error("lambda_error", error=str(e), event_data=event)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 