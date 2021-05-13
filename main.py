import json
from datetime import datetime

from utils.scrape import Tracker
from utils.send_email import Email
from utils.loggers import read_cfg
import utils.loggers as lg

# TODO:
# - Add regression for each stock
# - LSTM model and retraining  pipeline

if __name__ == '__main__':
	lg.app.info(f'\n\n------------------------------------------------------------------------------------')
	lg.app.info(f'Sending update for {datetime.today().strftime("%B %d, %Y")}')

	try:
		config = read_cfg()
		track = Tracker(config)
		mode = config.get('PARAMETERS', 'Mode').lower()

		# Update stocks portfolio
		if (mode == 'update'):
			with open(config.get('UPDATE', 'new stocks path')) as f:
				new_stocks = json.load(f)
				track.check_for_new(new_stocks)
			lg.app.info("New stock data updated in the portfolio")

		# Analyse portfolio and send email
		elif (mode == 'email'):
			if str(config.get('PARAMETERS', 'last update')) == track.today:
				lg.app.info(f'Analysis for {track.today} already exists!')
				Email(config, track.today, email_exists=True).send()
			else:
				shares_values, overall_top_gainers = track.scrape()
				total_market_value, market_value_change, gainers, losers = track.analyse(shares_values)
				email = Email(config,
							  track.today,
							  total_value = total_market_value,
							  value_change = market_value_change,
							  gainers = gainers,
							  losers = losers,
							  overall_gainers = overall_top_gainers,
							).send()

		# Only analyse portfolio
		elif (mode == 'analyse'):
			if str(config.get('PARAMETERS', 'last update')) == track.today:
				lg.app.info(f'Analysis for {track.today} already exists!')
			else:
				shares_values, overall_top_gainers = track.scrape()
				total_market_value, market_value_change, gainers, losers = track.analyse(shares_values)

		# Unknown mode
		else:
			raise RuntimeError(f"Unknown mode: {mode}")

		lg.app.info('Update for the day done!')

	except Exception as e:
		lg.app.error(f'Error encountered as {e}', exc_info=True)
		lg.app.debug(f'Could not send update for {datetime.today().strftime("%B %d, %Y")}')
