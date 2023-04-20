import boto3
import pickle
from sklearn.linear_model import LogisticRegression

s3 = boto3.client('s3')
bucket_name = 'alarm-ml-models-east'
file_key = '5_logistic_regression_v1.pkl'

def lambda_handler(event, context):
    city_resolvedAddress = 0.0 # 'Kyiv'
    day_temp = 3.3
    day_humidity = 80.8
    hour_windspeed = 10.8
    hour_conditions = 0.0 # 'sunny'
    city = 0.0 # 'Kyiv'
    
    print('test_1')
    local_file_path = '/tmp/model.pkl'
    s3.download_file(bucket_name, file_key, local_file_path)
    
    print('downloaded')
    
    # Load the saved model from the file
    with open(local_file_path, 'rb') as f:
        model = pickle.load(f)
    
    print('model is ready')
    
    new_data = [[city_resolvedAddress, day_temp, day_humidity, hour_windspeed, hour_conditions, city]]
    # new_data = new_data.apply(pd.to_numeric, errors='coerce')
    # X.fillna(0, inplace=True)
    
    predicted_labels = model.predict(new_data)

    # Print the predicted labels
    print(predicted_labels)
    
    first_value = str(predicted_labels[0])
    
    return {
        'statusCode': 200,
        'body': first_value
    }

if __name__ == "__main__":
    lambda_handler('', '')
