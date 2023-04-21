import boto3
import pickle
from sklearn.linear_model import LogisticRegression
import requests
from datetime import datetime

s3 = boto3.client('s3')
bucket_name = 'alarm-ml-models-east'
file_key = '5_logistic_regression_v1.pkl'

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

def save_prediction(region, date_of_prediction, value):
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
        'model_version': '2023-04-20'
    }

    response = table.put_item(Item=record)
    print('Saving prediction to database: ' + str(response['ResponseMetadata']['HTTPStatusCode']))

def process_region(region, model):
    print('start processing ' + region)
    
    city_resolvedAddress = 0.0 # 'Kyiv'
    day_temp = 3.3
    day_humidity = 80.8
    hour_windspeed = 10.8
    hour_conditions = 0.0 # 'sunny'
    city = 0.0 # 'Kyiv'
    
    weather_data = get_weather(region)
    
    # print(weather_data)
    day_temp = weather_data['days'][0]['temp']
    print('day_temp: ' + str(day_temp))
    
    day_humidity = weather_data['days'][0]['humidity']
    print('day_humidity: ' + str(day_humidity))
    
    hour_windspeed = weather_data['days'][0]['hours'][0]['windspeed']
    print('hour_windspeed: ' + str(hour_windspeed))
    
    new_data = [[city_resolvedAddress, day_temp, day_humidity, hour_windspeed, hour_conditions, city]]
    # new_data = new_data.apply(pd.to_numeric, errors='coerce')
    # new_data.fillna(0, inplace=True)
    
    predicted_labels = model.predict(new_data)
    first_value = str(predicted_labels[0])
    
    # Print the predicted value
    print(f'For {region} predicted value is {first_value}')
    
    now = datetime.now()
    dt_pred_string = now.strftime("%Y-%m-%d %H:%M:%S")
    save_prediction(region, dt_pred_string, str2bool(first_value))

def lambda_handler(event, context):
    print('starting lambda')
    
    local_file_path = '/tmp/model.pkl'
    s3.download_file(bucket_name, file_key, local_file_path)
    
    print('model downloaded')
    
    # Load the saved model from the file
    with open(local_file_path, 'rb') as f:
        model = pickle.load(f)
    
    print('model is ready')
    
    for region in regions:
        process_region(region, model)
    
    return {
        'statusCode': 200
    }

if __name__ == "__main__":
    lambda_handler('', '')
