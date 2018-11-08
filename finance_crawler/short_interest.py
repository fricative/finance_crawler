from dateutil.parser import parse
from bs4 import BeautifulSoup
import pandas as pd
import requests
import traceback


class ShortInterestCrawler:
    
    base_url = 'https://www.nasdaq.com/symbol/%s/short-interest'
    table_id = 'quotes_content_left_ShortInterest1_ShortInterestGrid'
    
    def __init__(self): 
        pass
    
    def crawl(self, tickers):
        """
        tickers: A list of stock tickers to retrieve data for
        
        returns a dataframe containing the four columns shown on the following example
        https://www.nasdaq.com/symbol/fb/short-interest with another column for ticker
        """
        
        error_tickers = []
        aggregate_df = pd.DataFrame(columns = ['ticker', 'settlement_date', 
                                               'short_interest', 'avg_daily_volume',
                                               'days_to_cover'])
        for idx, ticker in enumerate(tickers):
            try:
                ticker_url = self.base_url % ticker
                response = requests.get(ticker_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                table = soup.find('table', id=self.table_id)
                table_body = table.find('tbody')
                table_rows = table_body.find_all('tr')
                
                data_dict = {'settlement_date': [],
                             'short_interest': [],
                             'avg_daily_volume': [],
                             'days_to_cover': []}
                
                for row in table_rows:
                    
                    cells = row.findChildren('td')
                    data_dict['settlement_date'].append(parse(cells[0].getText()).date())
                    data_dict['short_interest'].append(cells[1].getText().replace(',', ''))
                    data_dict['avg_daily_volume'].append(cells[2].getText().replace(',', ''))
                    data_dict['days_to_cover'].append(cells[3].getText().replace(',', ''))
                    ticker_df = pd.DataFrame(data_dict)
                    ticker_df['ticker'] = ticker
            
                aggregate_df = pd.concat([aggregate_df, ticker_df], axis=0)
                print('Finished processing %sth ticker %s' % (idx,ticker))
                
            except AttributeError:
                print('Ticker %s has no short interest information available' % ticker)
            except Exception as ex:
                print('Encountered error processing ticker %s' % ticker)
                traceback.print_exc()
            finally:
                error_tickers.append(ticker)
                
        return aggregate_df, error_tickers


if __name__ == '__main__':
    
    # example
    tickers = ['FB', 'TSLA', 'NVDA']
    df, errors = ShortInterestCrawler().crawl(tickers)
    print(df)
    print(errors)