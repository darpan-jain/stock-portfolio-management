import codecs
import os
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

import utils.loggers as lg

class Email:
	def __init__(self, config, today, email_exists=False, **kwargs):
		self.config = config
		self.today = today
		self.email_path = 'utils/emails'
		self.data_path = self.config.get('PARAMETERS', 'csv path')
		if not email_exists:
			self.gainers, self.losers, self.overall_top_gainers = kwargs.get('gainers'), \
																  kwargs.get('losers'), \
																  kwargs.get('overall_gainers')
			self.total_value, self.market_value_change = kwargs.get('total_value'), \
														 kwargs.get('value_change')
			self.html_content = self.create_html()
			self.write_html_to_file()
		else:
			self.html_content = str(codecs.open(f'{self.email_path}/email_{self.today}.html').read())

		self.sender_address = config.get('EMAIL', 'sender email')
		self.sender_pass = config.get('EMAIL', 'sender pass')
		recipients = [config.get('EMAIL', 'receipients')]
		self.receiver_address = [elem.strip().split(',') for elem in recipients][0]

	def send(self):
			attachment_name = self.config.get('EMAIL', 'attachment name')
			message = MIMEMultipart()
			message['From'] = self.sender_address
			message['Subject'] = 'Stocks Portfolio Update'
			message.attach(MIMEText(self.html_content, 'html'))
			attach_file = open(f'{self.data_path}updated_stock_prices.csv', 'rb')
			payload = MIMEBase('application', 'octate-stream')
			payload.set_payload((attach_file).read())
			encoders.encode_base64(payload)
			payload.add_header('Content-Disposition', 'attachment', filename=attachment_name)
			message.attach(payload)

			session = smtplib.SMTP('smtp.gmail.com', 587)
			session.starttls()  # enable security
			session.login(self.sender_address, self.sender_pass)
			session.sendmail(self.sender_address, self.receiver_address, message.as_string())
			session.quit()
			lg.app.info(f'Email update for {self.today} sent to {self.receiver_address}')

	def create_html(self):
		if self.market_value_change < 0:
			value_change_color = '#ff0000'
			arrow = '&or;'
		else:
			value_change_color = '#0000ff'
			arrow = '&and;'

		# Style and formatting of df
		# gainers = gainers.style.applymap(self.color_negative_red, subset=['Price Change'])
		# losers = losers.style.applymap(self.color_negative_red, subset=['Price Change'])

		html_content = f'''
				<html>
				 <body>
					<h2 style="text-align: left;">
					<strong>
						<span style="color: #000000;">
						DAILY STOCK VALUE UPDATE
						</span>
					</strong></h2>
					<hr>
					<h3> Date: {self.today}\n\n</h3>
					<h3>Total Market Value = <span style="color: #3366ff;">₹{self.total_value}</span>\n\n</h3>
					<h3>Change since previous day = <span style="color: {value_change_color};"> {arrow} ₹{abs(self.market_value_change)}</span>\n\n</h3>
					<h3><span style="color: #99cc00;">Top Gainers</span></h3>
					<p>\n{self.gainers.to_html(index=False)}\n\n</p>
					<h3><span style="color: #ff0000;">Top Losers</span></h3>
					<p>\n{self.losers.to_html(index=False)}\n\n</p>
					<hr />
					<h3>Top Gainers in NSE Today</h3>
					<p>\n{self.overall_top_gainers.to_html(index=False)}\n\n</p>
				  </body>
				</html>
				'''

		## To use self.stylize: <p>\n{self.stylize(self.losers)}\n\n</p>
		return html_content

	def write_html_to_file(self):
		if not os.path.exists(self.email_path):
			os.mkdir(self.email_path)
		filename = f"{self.email_path}/email_{self.today}.html"
		with open(filename,"w+") as f:
			f.write(self.html_content)
		lg.app.debug(f'HTML for {self.today} stored on disk.')

	def stylize(self, df):
		return (df
				.style
				.applymap(self.color_negative_red, subset=['% Change'])
				.set_table_attributes('border="1" class="pure-table"')
				.render()
				)

		# html = (
		# 	df.style
		# 	  .format(percent)
		# 	  .applymap(color_negative_red, subset=['col1', 'col2'])
		# 	  .set_properties(**{'font-size': '9pt', 'font-family': 'Calibri'})
		# 	  .bar(subset=['col4', 'col5'], color='lightblue')
		# 	  .render()
		# )

	def color_negative_red(self, value):
		"""
		Colors elements in a dateframe
		green if positive and red if
		negative. Does not color NaN
		values.
		"""
		if value < 0:
			color = 'red'
		elif value > 0:
			color = 'green'
		else:
			color = 'black'
		return 'color: %s' % color