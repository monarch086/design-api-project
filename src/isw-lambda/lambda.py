import json
import requests
import re
import time
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
import json
from collections import namedtuple

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


def lambda_handler(event, context):
    
    
    url = get_url(date.today())
    if event and event.get('date'):
        print(event['date'])
        url = get_url(datetime.strptime(event.get('date'), "%Y-%m-%d"))
            
            
    response = requests.get(url)
    
    ok = response.ok
    print('OK' if response.ok else 'Not OK' )
    
    if not ok:
        return ''
        
    else:
        final_data = parse_day(response.text)
        # print(final_data[:5])
        return "\n".join(final_data)
