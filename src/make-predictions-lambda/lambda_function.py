import boto3
import pickle
from sklearn.linear_model import LogisticRegression
import requests
from datetime import datetime, timedelta
import fnmatch
import re

s3 = boto3.client('s3')
bucket_name = 'alarm-ml-models-east'
file_mask = '5_logistic_regression_*.pkl'

weather_url = 'https://s5uukglwungpg3v5pb6jjnrl7m0fxbaw.lambda-url.us-east-1.on.aws/'
regions = ['Simferopol', 'Vinnytsia', 'Lutsk', 'Dnipro', 'Donetsk', 'Zhytomyr', 'Uzhgorod',
'Zaporozhye', 'Ivano-Frankivsk', 'Kyiv', 'Kropyvnytskyi', 'Luhansk', 'L\'viv', 'Mykolaiv',
'Odesa', 'Poltava', 'Rivne', 'Sumska', 'Ternopil', 'Kharkiv', 'Kherson', 'Khmelnytskyi',
'Cherkasy', 'Chernivtsi', 'Chernihiv']

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

def save_prediction(region, date_of_prediction, value, model_date):
    table_name = 'predictions'

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    record = {
        'date_created': dt_string,
        'region': region,
        'date_of_prediction': date_of_prediction,
        'is_alarm': value,
        'model_version': model_date
    }

    response = table.put_item(Item=record)
    print('Saving prediction to database: ' + str(response['ResponseMetadata']['HTTPStatusCode']))

def process_hour(region, data, model, pred_date, model_date):
    predicted_labels = model.predict(data)
    first_value = str(predicted_labels[0])

    save_prediction(region, pred_date, str2bool(first_value), model_date)

def process_region(region, model, model_date):
    print('start processing ' + region)
    
    city_resolvedAddress = 0.0 # 'Kyiv'
    day_temp = 0.0
    day_humidity = 0.0
    hour_windspeed = 0.0
    hour_conditions = 0.0 # 'sunny'
    city = 0.0 # 'Kyiv'
    
    weather_data = get_weather(region)
    
    data = [[city_resolvedAddress, day_temp, day_humidity, hour_windspeed, hour_conditions, city]]
    now = datetime.now()

    for i in range(12):
        print(f"Iteration {i + 1}")
        
        day_temp = weather_data['days'][0]['temp']
        day_humidity = weather_data['days'][0]['humidity']
        hour_windspeed = weather_data['days'][0]['hours'][i]['windspeed']
        
        prediction_date = now + timedelta(hours = i)
        prediction_date_str = prediction_date.strftime("%Y-%m-%d %H:%M:%S")
        process_hour(region, data, model, prediction_date_str, model_date)

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
    
    for region in regions:
        process_region(region, model, model_date)
    
    return {
        'statusCode': 200
    }

if __name__ == "__main__":
    lambda_handler('', '')
