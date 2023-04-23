import boto3
import pickle
from sklearn.linear_model import LogisticRegression
import requests
from datetime import datetime, timedelta
import fnmatch
import re
import json
import asyncio
import aiohttp
import time
import math
from dateutil import parser
from functools import reduce


s3 = boto3.client('s3')
bucket_name = 'alarm-ml-models-east'
current_alarms_url = "https://api.ukrainealarm.com/api/v3/alerts"
file_mask = '5_logistic_regression_*.pkl'

alarm_key = '5793d984:7ce216a2d140061a49dcc9140c182522'
weather_url = 'https://s5uukglwungpg3v5pb6jjnrl7m0fxbaw.lambda-url.us-east-1.on.aws/'
history_url = 'https://api.ukrainealarm.com/api/v3/alerts/regionHistory?regionId='

region_to_alert_api_id = {
    'Simferopol': 9999, 'Vinnytsia': 4, 'Lutsk': 8, 'Dnipro': 9, 'Donetsk': 28, 
    'Zhytomyr': 10,  'Uzhgorod': 11, 'Zaporozhye': 12, 'Ivano-Frankivsk': 13, 
    'Kyiv': 14, 'Kropyvnytskyi': 15, 'Luhansk':16, 'L\'viv': 27, 'Mykolaiv': 17, 
    'Odesa': 18, 'Poltava': 19, 'Rivne': 5, 'Sumska': 20, 'Ternopil': 21, 'Kharkiv': 22, 
    'Kherson': 23, 'Khmelnytskyi': 3, 'Cherkasy': 24, 'Chernivtsi': 26, 'Chernihiv': 25}

regions = list(region_to_alert_api_id.keys())

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def get_weather(region):
    print('getting weather')
    url = weather_url + "?Location=" + region
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Getting weather ERROR: {response.status_code}")

def get_hours(data, now):
    bound = now - timedelta(hours=24.)

    def read_date(str):
        return parser.parse(str)
    def hours(alert):
        start = max(read_date(alert['startDate']), bound)
        end = now if alert['isContinue'] == True else read_date(alert['endDate'])
        return math.ceil((end - start).total_seconds() / 3600)
    filtered = filter(lambda x: x['alertType'] == 'AIR' and (x['isContinue'] == True or read_date(x['endDate']) > bound), data['alarms'])
    return sum(map(hours, filtered))

async def get_hours_for_region(region_name, now, session: aiohttp.ClientSession):
    url = history_url + str(region_to_alert_api_id[region_name])
    try:
        async with session.get(url=url) as response:
            resp = await response.json()
            return (region_name, get_hours(resp[0], now))
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))

async def get_history():
    now = datetime.now()
    async with aiohttp.ClientSession(headers={'accept': 'application/json', 'Authorization': alarm_key}) as session:
        lst = await asyncio.gather(*[get_hours_for_region(region, now, session) for region in regions])
        return dict((x, y) for x, y in lst)

def get_num_regions():
    response = requests.get(current_alarms_url, headers= {'accept': 'application/json', 'Authorization': alarm_key})
    if response.status_code == 200:
        data = response.json()
        active_alerts = reduce(list.__add__, map(lambda x: x['activeAlerts'], data))
        print(active_alerts)
        filtered = list(filter(lambda x: x['regionType'] == 'State' and x['type'] == 'AIR', active_alerts))
        return len(filtered)
    else:
        print(f"Getting current_num_regions ERROR: {response.status_code}")


def save_prediction(now_string, region, model_date, data):
    table_name = 'predictions_v2'

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    record = {
        'region': region,
        'date_created': now_string,
        'model_version': model_date,
        'data': data
    }

    response = table.put_item(Item=record)
    print('Saving prediction to database: ' + str(response['ResponseMetadata']['HTTPStatusCode']))

def process_region(region, model, model_date, num_regions, hours_last_day):
    print('start processing ' + region + 'with num regions ' + str(num_regions) + 'and hours' + str(hours_last_day))
    
    city_resolvedAddress = 0.0 # 'Kyiv'
    day_temp = 0.0
    day_humidity = 0.0
    hour_windspeed = 0.0
    hour_conditions = 0.0 # 'sunny'
    city = 0.0 # 'Kyiv'
    
    weather_data = get_weather(region)
    now = datetime.now()
    now_string = now.strftime("%Y-%m-%d %H:%M:%S")
    
    prediction_data = {}
    lst = []
    for i in range(12):
        # print(f"Iteration {i + 1}")
        
        day_temp = weather_data['days'][0]['temp']
        day_humidity = weather_data['days'][0]['humidity']
        hour_windspeed = weather_data['days'][0]['hours'][i]['windspeed']
        data = [[city_resolvedAddress, day_temp, day_humidity, hour_windspeed, hour_conditions, city, num_regions, hours_last_day]]
        
        prediction_date = now + timedelta(hours = i)
        prediction_date_str = prediction_date.strftime("%Y-%m-%d %H:%M:%S")

        predicted_labels = model.predict(data)
        first_value = str(predicted_labels[0])
        lst.append(first_value)
        prediction_data[prediction_date_str] = str2bool(first_value)
    save_prediction(now_string, region, model_date, json.dumps(prediction_data))
    print(lst)

def find_latest_model():
    match_models = []
    
    # List objects in the bucket with the given prefix
    response = s3.list_objects_v2(Bucket=bucket_name)
    
    # Check if there are any objects in the response
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            
            if fnmatch.fnmatch(key, file_mask):
                match_models.append(key)
                
        match_models.sort(reverse=True)
        
        if len(match_models) > 0:
            print(f'Found latest model: {match_models[0]}')
            return match_models[0]

    return None

def get_model_date(filename):
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    
    match = re.search(date_pattern, filename)

    if match:
        date_string = match.group(0)
        print("Model date:", date_string)
        
        return date_string
    else:
        print("No model date found")
        
        return 'default'

def lambda_handler(event, context):
    print('starting lambda')
    
    local_file_path = '/tmp/model.pkl'
    
    latest_model = find_latest_model()
    if (not bool(latest_model)):
        return

    s3.download_file(bucket_name, latest_model, local_file_path)
    
    print('model downloaded')
    
    model_date = get_model_date(latest_model)
    
    # Load the saved model from the file
    with open(local_file_path, 'rb') as f:
        model = pickle.load(f)
    
    print('model is ready')
    
    history = asyncio.run(get_history())
    print('history')
    print(history)
    num_regions = get_num_regions()
    print('num_regions')
    print(num_regions)
    for region in regions:
        process_region(region, model, model_date, num_regions, history[region])
    
    print('history')
    print(history)
    print('num_regions')
    print(num_regions)
    
    return {
        'statusCode': 200
    }

if __name__ == "__main__":
    lambda_handler('', '')