import pandas as pd

updated_stock_prices = pd.read_csv('../data/updated_stock_prices.csv')
symbols_list = updated_stock_prices['Company Symbol']
