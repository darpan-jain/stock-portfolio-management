import ssl
import time
from nsetools import Nse
import pandas as pd
from bsedata.bse import BSE
from datetime import datetime

import utils.loggers as lg

ssl._create_default_https_context = ssl._create_unverified_context

# Literal constants
DAILY_CHANGE = "Daily Change"
PERCENT_CHANGE = "% Change"
NUM_OF_SHARES = "Number of Shares"
COMPANY_NAME = "Company Name"
COMPANY_SYMBOL = "Company Symbol"
VOLUME = "Volume"


class Tracker:

	def __init__(self, config):
		self.config = config
		self.data_path = self.config.get("PARAMETERS", "csv path")
		self.last_update = str(self.config.get("PARAMETERS", "last update"))
		self.today = datetime.today().strftime("%B %d, %Y")
		# self.yesterday = (datetime.today() - timedelta(days=1)).strftime("%B %d, %Y")
		self.nse = Nse()
		self.bse = BSE()
		# self.bse.updateScripCodes()
		self.bse_stocks_scripcodes = {
			"CALSREF": "526652",
			"MADHUCON": "531497",
			"LITL": "532778",
			"UDAICEMENT": "530131",
			"RTNINFRA": "534597"
		}
		self.error_count = []

	def scrape(self) -> (pd.DataFrame, list):
		updated_stock_prices = pd.read_csv(f"{self.data_path}updated_stock_prices.csv")
		symbols_list = updated_stock_prices[COMPANY_SYMBOL]
		lg.app.info(f"Number of companies = {len(symbols_list)}")

		tic = datetime.now()
		_, curr_prices, total_traded_volume = self.fetch_stock_details(symbols_list)
		toc = datetime.now()

		lg.app.debug(f"Total time to fetch stock prices = {round((toc - tic).total_seconds(), 3)} secs")
		if len(self.error_count) > 0:
			lg.app.debug(f"Error encountered for {len(self.error_count)} companies: {self.error_count}")
		updated_stock_prices[self.today] = curr_prices
		updated_stock_prices[VOLUME] = total_traded_volume
		lg.app.debug(f"Prices fetched and stored in df. Shape = {updated_stock_prices.shape}")

		# Get top performers at NSE
		overall_top_gainers = self.nse.get_top_gainers()
		overall_top_gainers = pd.DataFrame(overall_top_gainers, columns=["symbol", "lowPrice", "highPrice"])
		lg.app.debug(f"Top gainers from NSE fetched. Shape = {overall_top_gainers.shape}")
		return updated_stock_prices, overall_top_gainers

	def analyse(self, shares_value, update_date_in_config=True) -> (float, float, pd.DataFrame, pd.DataFrame):
		lg.app.debug(
			f"Analysing updated stocks prices for {self.today} with update_data_in_config = {update_date_in_config}")
		price_change = shares_value[self.today] - shares_value[self.last_update]
		shares_value[DAILY_CHANGE] = round(price_change, 4)
		shares_value[PERCENT_CHANGE] = round(((price_change / shares_value[self.last_update]) * 100), 2)

		# Sort stocks based on percent change
		shares_value = shares_value.sort_values(by=[DAILY_CHANGE], ascending=False)
		total_market_value = round(sum(shares_value[self.today] * shares_value[NUM_OF_SHARES]), 2)
		market_value_change = round(total_market_value - round(sum(shares_value[self.last_update] * shares_value[
			NUM_OF_SHARES]), 2), 2)

		# Update columns order of csv
		new_order = shares_value.columns.tolist()
		new_order.insert(5, new_order.pop(new_order.index(self.today)))
		shares_value = shares_value[new_order]

		# Write to csv before you filter zero value stocks
		shares_value.to_csv("utils/data/updated_stock_prices.csv", index=False, header=True)
		lg.app.debug("Dataframe dumped to disk.")

		# Remove stocks which are delisted or price = 0
		shares_value = shares_value[shares_value[self.today] > 0]

		# Center justify headers in Dataframe
		pd.set_option("colheader_justify", "center")

		gainers = shares_value[[COMPANY_NAME, NUM_OF_SHARES, self.last_update, self.today, PRICE_CHANGE,
								PERCENT_CHANGE, VOLUME]].head(6)
		losers = shares_value[[COMPANY_NAME, NUM_OF_SHARES, self.last_update, self.today, PRICE_CHANGE,
							   PERCENT_CHANGE, VOLUME]].tail(6)
		lg.app.debug(f"Total market value today = ₹{total_market_value}")
		lg.app.debug(f"Value update since {self.last_update} = ₹{market_value_change}")

		# Update the last update date in config
		if update_date_in_config:
			self.update_date()

		return total_market_value, market_value_change, gainers, losers

	def check_for_new(self, new_companies):
		try:
			updated_stock_prices = pd.read_csv(f"{self.data_path}updated_stock_prices.csv")
			companies = updated_stock_prices[COMPANY_SYMBOL].tolist()
			for symbol in new_companies.keys():
				# Check if company exists in portfolio
				if symbol not in companies:
					lg.app.info(f"Fetch info for {symbol}...")
					updated_stock_prices = self.add_to_portfolio(symbol, new_companies[symbol],
																 updated_stock_prices)

			# Check if num of shares for existing company changes
			# elif 0 < new_companies[symbol] != updated_stock_prices.loc(COMPANY_SYMBOL == symbol):
			# 	lg.app.info(f"Number of shares for {symbol} to be changed from "
			# 				f"{updated_stock_prices[COMPANY_SYMBOL][NUM_OF_SHARES]} to "
			# 				f"{new_companies[symbol]}")
			# 	updated_stock_prices = updated_stock_prices[COMPANY_SYMBOL][NUM_OF_SHARES] = new_companies[symbol]

			company_data = updated_stock_prices.filter([COMPANY_SYMBOL, COMPANY_NAME, NUM_OF_SHARES], axis=1)
			updated_stock_prices.to_csv(f"{self.data_path}updated_stock_prices.csv", index=False, header=True)
			company_data.to_csv(f"{self.data_path}company_share_data.csv", index=False)

			lg.app.debug(f"Stocks CSV updated with new entries : {new_companies.keys()}")
			self.update_new_stocks_status(str(False))

		except Exception as e:
			lg.app.error(f"Error while checking for new company data: {e}", exc_info=True)

	def add_to_portfolio(self, symbol, num_shares, updated_stock_prices):
		# TODO: Revisit logic for update number of stocks
		name, last_price, volume = self.get_stock(symbol)
		new_row = {COMPANY_NAME: name,
				   COMPANY_SYMBOL: symbol,
				   NUM_OF_SHARES: num_shares,
				   self.last_update: last_price,
				   DAILY_CHANGE: 0,
				   PERCENT_CHANGE: 0,
				   VOLUME: 0
				   }

		lg.app.debug(f"Adding {new_row[COMPANY_NAME]} to portfolio")
		if self.today in updated_stock_prices.columns:
			new_row[self.today] = last_price
		updated_stock_prices = updated_stock_prices.append(new_row, ignore_index=True)

		return updated_stock_prices

	def fetch_stock_details(self, symbols_list):
		curr_prices = []
		total_traded_volume = []
		names = []

		for stock_symbol in symbols_list:
			try:
				tic = time.process_time()
				name, last_price, volume = self.get_stock(stock_symbol)
				toc = time.process_time()
				lg.app.debug(f"Time to fetch {stock_symbol} prices = {round((toc - tic) * 1000, 2)} ms")

				names.append(name)
				curr_prices.append(last_price)
				total_traded_volume.append(volume)

			except IndexError as err:
				lg.app.warning(f"{err} during fetching {stock_symbol}")
				self.error_count.append(stock_symbol)
				names.append("")
				curr_prices.append(0)
				total_traded_volume.append("")
				continue

			except Exception as ex:
				lg.app.error(f"Error encountered: {ex}", exc_info=True)
				break

		return names, curr_prices, total_traded_volume

	def get_stock(self, stock_symbol):
		lg.app.info(f"Fetching metrics for {stock_symbol}...")

		# NSE Stock
		q = self.nse.get_quote(stock_symbol)

		if not q:
			# BSE stock
			q = self.bse.getQuote(self.bse_stocks_scripcodes[stock_symbol])
			# Add data for BSE Stock to arrays
			last_price = float(q["currentValue"])
			volume = q["totalTradedQuantity"]
			name = q["companyName"]

			# Stock data not found
			if not q:
				lg.app.warning(f"No data found on {stock_symbol}")
				last_price = 0
				volume = 0
				name = ""

		# Add data for NSE Stock to arrays
		else:
			last_price = q["lastPrice"]
			volume = q["totalTradedVolume"]
			name = q["companyName"]

		return name, last_price, volume

	def update_date(self):
		# update_date = self.today.encode(encoding='UTF-8')
		self.config.set("PARAMETERS", "last update", str(self.today))
		with open("utils/configs/config.ini", "w") as configfile:
			self.config.write(configfile)
		lg.app.info(f"Config updated for {self.today}")

	def update_new_stocks_status(self, status):
		self.config.set("UPDATE", "update stocks", status)
		with open("utils/configs/config.ini", "w") as configfile:
			self.config.write(configfile)
		lg.app.info(f"Status for new stocks data updated to {status}")
