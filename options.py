from ryan_tools import *
import pandas_datareader.data as web
from pandas_datareader.data import Options
import fuckit

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
    #data['lasttradedate'] = data['lasttradedate'].apply(datetime.datetime.fromtimestamp )
    if stock_prices:
        data = get_stock_prices(data, ticker)
    data.index = data['strike']
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
    
    

def find_point(data):

    for index in data.index:

        bid = data.loc[index, 'bid']
        ask = data.loc[index, 'ask']
        
        with fuckit:
            data.loc[index, 'profit 0.5'] = bid -  data.loc[index - 0.5, 'ask']

        with fuckit:
            data.loc[index, 'profit 1'] = bid -  data.loc[index - 1, 'ask']
            
        with fuckit:
            data.loc[index, 'profit 2'] = bid -  data.loc[index - 1.5, 'ask']
            
        with fuckit:
            data.loc[index, 'profit 2'] = bid -  data.loc[index - 2, 'ask']

    return data

def timevalue(data, start, end):
    data = data[(data['days_left'] == start) | (data['days_left'] == end)]
    data = data[data['lasttradedate'].apply(lambda x: read_date(get_date_str(x))) == read_date(get_date_str(datetime.datetime.today()))]
    
    data['unique'] = data['strike'].apply(str) + data['type'].apply(str)
    data = data[data['unique'].duplicated( keep = False)]
    puts = data[data['type'] == 'put']
    calls = data[data['type'] == 'call']
    print('ALL')
    print(data.groupby('days_left')['lastprice'].mean())

    print('CALLS')
    print(calls.groupby('days_left')['lastprice'].mean())

    print('PUTS')
    print(puts.groupby('days_left')['lastprice'].mean())
    return data
    
def the_spot(data):
    data.plot('strike', 'bid', kind = 'scatter')
data = download('spy')



