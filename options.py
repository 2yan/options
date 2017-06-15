from ryan_tools import *
import pandas_datareader.data as web
from pandas_datareader.data import Options

def download(ticker, stock_prices = False):
    data = Options(ticker, 'yahoo').get_all_data()
    body = pd.DataFrame(list(data['JSON']))
    data = pd.DataFrame(list(data.index), columns = data.index.names )
    data = data.merge(body,  left_on = 'Symbol' , right_on = 'contractSymbol' )
    del data['contractSymbol']
    del data['strike']
    del data['expiration']
    
    data.columns = data.columns.str.lower()
    data['days_left'] = ( data['expiry'] - datetime.datetime.today()).dt.days
    data['lasttradedate'] = data['lasttradedate'].apply(datetime.datetime.fromtimestamp )
    if stock_prices:
        data = get_stock_prices(data, ticker)
    return data



def get_stock_prices(options_data, ticker):
    options_data['temp'] = options_data['lasttradedate'].apply(get_date_str).apply(read_date)
    start = options_data['lasttradedate'].min()
    end = options_data['lasttradedate'].max()
    stock_data = web.DataReader(ticker, 'google', start = start, end = end )
    stock_data['temp'] = stock_data.index
 
    final = options_data.merge(stock_data, how = 'left', left_on ='temp', right_on  = 'temp' )
    final = final.reset_index()
    del final['temp']
    del final['index']
    return final




def get_project_value(data):
    result = data.copy()
    calls = data['type'] == 'call'
    puts = data['type'] == 'put'
    result['value'] = 0
    result.loc[calls, 'value'] = data.loc[calls , 'Close'] - data.loc[calls, 'strike']
    result.loc[puts, 'value'] = data.loc[puts, 'strike'] - data.loc[puts , 'Close']
    return result['value']
    
    

data = download('aapl', True)
data['value'] = get_project_value(data)
data['extra_value'] = data['lastprice'] - data['value']
