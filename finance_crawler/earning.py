from copy import deepcopy
from datetime import date, timedelta
import json
import random
import time

import pandas as pd
from selenium import webdriver


class EarningCrawler:
    
    api = 'https://www.bloomberg.com/markets/api/calendar/earnings/%s?locale=en&date=%s'
    
    def __init__(self, chrome_driver_path):
        self.driver_path = chrome_driver_path
    
    def crawl_market(self, market, start_date, end_date):
        
        days_in_between = (end_date - start_date).days + 1
        dates = [start_date + timedelta(i) for i in range(days_in_between)]
        data = dict()
        driver = webdriver.Chrome(self.driver_path)
        
        for day in dates:
            date_url = self.api % (market, day.isoformat())
            try:
                driver.get(date_url)
                content = driver.find_element_by_tag_name("pre")
                json_data = json.loads(content.text)
                events = json_data.get('events')
                if events:
                    events = deepcopy(events)
                    for event in events:
                        del event['company']['_links']
                    
                    json_str = json.dumps(events)
                    df = pd.read_json(json_str)
                    df['ticker'] = df['company'].apply(lambda x: x['ticker'])
                    df['name'] = df['company'].apply(lambda x: x['name'])
                    df['timestamp'] = df['eventTime'].apply(lambda x: x['dateTime'])
                    df['market_time'] = df['eventTime'].apply(lambda x: x['marketTime'])
                    df['actual_eps'] = df['eps'].apply(lambda x: x['actual'])
                    df['estimated_eps'] = df['eps'].apply(lambda x: x['estimate'])
                    df['fiscal_period'] = df['fiscalPeriod'].apply(lambda x: x['period'])
                    df['fiscal_year'] = df['fiscalPeriod'].apply(lambda x: x['year'])
                    
                    data[day.isoformat()] = df.loc[:, ['ticker', 'name', 'timestamp',
                                                'market_time', 'actual_eps', 'estimated_eps',
                                                'fiscal_period', 'fiscal_year']]
            except Exception:
                print('Error encountered when processing market %s, business date: %s' % (market, day))
            time.sleep(3 + random.random() * 2)     
        
        driver.quit()
        df = pd.concat(data.values(), axis=0)
        return df


if __name__ == '__main__':
    
    # Quick Example
    market = 'JP'    # supported market 'US', 'UK', 'DE', 'JP', 'AU'
    start_date = date(2018,11,1)
    end_date = date(2018,11,9)
    
    driver_path = '/home/fricative/finance_crawler/finance_crawler/chromedriver'
    crawler = EarningCrawler(driver_path)
    result = crawler.crawl_market(market, start_date, end_date)
