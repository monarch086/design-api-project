import json
import boto3
import pickle
from datetime import datetime, timedelta
import fnmatch
import re
from boto3.dynamodb.conditions import Key, Attr

regions = ['Simferopol', 'Vinnytsia', 'Lutsk', 'Dnipro', 'Donetsk', 'Zhytomyr', 'Uzhgorod',
'Zaporozhye', 'Ivano-Frankivsk', 'Kyiv', 'Kropyvnytskyi', 'Luhansk', 'L\'viv', 'Mykolaiv',
'Odesa', 'Poltava', 'Rivne', 'Sumska', 'Ternopil', 'Kharkiv', 'Kherson', 'Khmelnytskyi',
'Cherkasy', 'Chernivtsi', 'Chernihiv']


s3 = boto3.client('s3')
bucket_name = 'alarm-ml-models-east'
file_mask = '5_logistic_regression_*.pkl'


    
def get_predictions_v2(region):
    table_name = 'predictions_v2'

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    now = datetime.now() - timedelta(hours=1, minutes=10)
    now_string = now.strftime("%Y-%m-%d %H")
    
    response = table.query(
        KeyConditionExpression=Key('region').eq('Dnipro') & Key('date_created').gte(now_string),
        ScanIndexForward=False,
        Limit=1
    )
    
    data = response["Items"]
    
    train_time = ''
    prediction_time = ''
    
    if len(data):
        train_time = data[0]["model_version"]
        prediction_time = data[0]["date_created"]
    
    return train_time, prediction_time, {
        region: json.loads(data[0]["data"])
    }


def lambda_handler(event, context):
    region = "all"
    
    if event and event.get('queryStringParameters') and event.get('queryStringParameters').get('region'):
        region = event["queryStringParameters"]['region']
        
        
    if not region in regions:
        region = 'all'
        
    if region == 'all':
        
        train_time = ''
        prediction_time = ''
        regions_forecast = {}
        
        for r in regions:
            train_time, prediction_time, forecast = get_predictions_v2(r)
            regions_forecast[r] = forecast[r]
        
        return {
            'statusCode': 200,
            'body': {
                'last_model_train_time': train_time,
                'last_prediction_time': prediction_time,
                'regions_forecast': regions_forecast
            }
        }
    
    else:
        train_time, prediction_time, forecast = get_predictions_v2(region)
        return {
            'statusCode': 200,
            'body': {
                'last_model_train_time': train_time,
                'last_prediction_time': prediction_time,
                'regions_forecast': forecast
            }
        }
    
    
