import requests
import re
import time
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
import json
from collections import namedtuple
import boto3

pattern = r'\[\d+\]'

years = [2023]

def get_year_str(year):
    if year == 2022:
        return ''
    return f'-{year}'

months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

def get_month_str(month):
    return months[month - 1]

def get_url(dat):
    # mb need to adjust the link a bit idk
    base_link = 'https://www.understandingwar.org/backgrounder/russian-offensive-campaign-assessment'
    year_str = get_year_str(dat.year)
    month_str = get_month_str(dat.month)
    return f'{base_link}-{month_str}-{dat.day}{year_str}'

def crawl(input):
    soup = BeautifulSoup(input, features="html.parser")
    content = soup.body
    data = []

    for tag in content.find_all(['p', 'li']):
        if tag.find('a'):
            continue

        if not tag.find(string=True):
            continue

        data.append(tag)
    
    return data

def extract_text_raw(tags):
    final_data = []

    for tag in tags:
        if tag.name == 'li':
            
            final_data.append(re.sub(pattern, '', tag.text if tag.text else ''))
            continue
        strong = tag.find_all('strong')
        if strong:
            count = len(strong)
            if count == 1:
                strong_tag = tag.find('strong')
                strong_sibling = strong_tag.next_sibling

                if strong_sibling:
                    final_data.append(re.sub(pattern, '', strong_tag.text if strong_tag.text else ''))
                    final_data.append(re.sub(pattern, '', strong_sibling.text if strong_sibling.text else ''))
                else:
                    final_data.append(re.sub(pattern, '', tag.text if tag.text else ''))
            else:
                final_data.append(re.sub(pattern, '', tag.text if tag.text else ''))
        else:
            final_data.append(re.sub(pattern, '', tag.text if tag.text else ''))
            
            
    final_data = [x for x in final_data if x]
    final_data = [name for name in final_data if name.strip()]
    # final_data = [line for line in final_data if 'http' in line]
            
    return final_data

def parse_day(input):
    res = crawl(input)
    final_data = extract_text_raw(res)  
    return final_data

def save_report(report_date, report):
    table_name = 'isw-reports'

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    record = {
        'date': datetime.strftime(report_date, "%Y-%m-%d"),
        'report': report
    }

    response = table.put_item(Item=record)
    print('Saving report to database: ' + str(response['ResponseMetadata']['HTTPStatusCode']))

def lambda_handler(event, context):
    report_date = date.today() - timedelta(days=1)

    if event and event.get('date'):
        print(event['date'])
        report_date = datetime.strptime(event['date'], "%Y-%m-%d")

    url = get_url(report_date)
    response = requests.get(url)
    
    ok = response.ok
    print('OK' if response.ok else 'Not OK' )
    
    final_data = ''
    
    if ok:
        parsed_response = parse_day(response.text)
        final_data = "\n".join(parsed_response)
        save_report(report_date, final_data)

    return final_data

