import json
import boto3
import os
import structlog
from typing import Any, Dict, Optional
from pydantic import BaseModel, ValidationError

# LocalStackのエンドポイントを設定
endpoint_url: str = 'http://localstack:4566'
region_name: str = 'us-east-1'

# structlogの設定
logger = structlog.get_logger()

# S3クライアントの初期化
s3 = boto3.client('s3', endpoint_url=endpoint_url, region_name=region_name)

# DynamoDBクライアントの初期化
dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url, region_name=region_name)

# Pydanticモデルを定義
class EventModel(BaseModel):
    key: str
    bucket_name: str
    additional_data: Optional[dict] = None

def lambda_handler(event: Dict[str, Any], context: Optional[Any]) -> Dict[str, Any]:
    try:
        # Pydanticでeventを検証
        event_data = EventModel(**event)

        # リクエストのログ
        logger.info("lambda_request", event_data=event_data.dict())
        
        # レスポンスの作成
        response: Dict[str, Any] = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Hello from Lambda!',
                'event': event_data.dict()
            })
        }
        
        # レスポンスのログ
        logger.info("lambda_response", response=response)
        return response
        
    except ValidationError as ve:
        # バリデーションエラーをログに記録
        logger.error("validation_error", error=str(ve))
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': "Invalid input format",
                'details': str(ve)
            })
        }
    except Exception as e:
        # エラーのログ
        logger.error("lambda_error", error=str(e), event_data=event)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
