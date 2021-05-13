from datetime import date
import pandas as pd
import nsepy

df = pd.read_csv('data/company_share_data.csv')
symbols = df['Company Symbol']
names = df['Company Name']

for sym,name in zip(symbols,names):
	try:
		history = nsepy.get_history(symbol=f'{sym}', start=date(2000,1,1), end=date(2020,7,28))
		history.to_csv(f'data/stock_history/{name}.csv')
		print(f'History for {name} collected!')
	except Exception as e:
		print(f'Exception while collecting data for {name}: {e}')

print('Stock history fetching complete!')
