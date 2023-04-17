import pandas as pd
import plotly.express as px
import yfinance as yf
from tabulate import tabulate
import os, json, hashlib

expense_ratio = 1/100
daily_expense_ratio = expense_ratio/365 # approximately

def get_data(ticker, period):

	args = {
		'tickers': ticker,
		'interval': '1d'
	}

	if isinstance(period, str):
		args['period'] = period
	
	else:
		args['start'] = period[0]
		args['end'] = period[1]

	args_json = json.dumps(args)

	hash = hashlib.md5(args_json.encode('utf-8')).hexdigest()

	filename = 'data/' + hash + '.csv'

	if not os.path.exists(filename):

		df = yf.download(**args)

		# Save to CSV
		df.to_csv(filename)

	else:
		df = pd.read_csv(filename)

	# Drop unnecessary columns
	df = df.drop(columns=['Open', 'High', 'Low', 'Adj Close', 'Volume'])

	return df

def calculate_leverage(data, leverage):

	leverage_data = []

	last_value = None

	for index, value in enumerate(data):

		leverage_value = value

		if last_value:
			
			appreciation = (value / last_value) - 1

			leverarage_appreciation = appreciation * leverage

			last_leverage_value = leverage_data[index-1]

			leverage_value = last_leverage_value * (1 + leverarage_appreciation)

			# Discount ER
			leverage_value -= (leverage_value * daily_expense_ratio)

			if leverage_value < 0:
				leverage_value = 0

		leverage_data.append(leverage_value)

		last_value = value

	return leverage_data

def run(ticker, leverage_levels, period = 'max', plot = False):

	data = get_data(ticker, period)
	
	close_values = data['Close']

	last_close = close_values.iloc[-1]

	table_data = [
		['#', 'No Leveraged'],
		['End Value (US$)', last_close],
		['Appreciation (%)', '-']
	]

	plot_y = ['Close']
	
	for level in leverage_levels:

		c = 'Leverage_' + str(level) + 'x'

		leveraged_data = calculate_leverage(data['Close'], level)
		leveraged_last_close = round(leveraged_data[-1], 3)
		leveraged_appreciation = round(((leveraged_last_close / last_close) - 1) * 100, 3)

		table_data[0].append(c)
		table_data[1].append(leveraged_last_close)
		table_data[2].append(leveraged_appreciation)

		data[c] = leveraged_data

		plot_y.append(c)

	print(tabulate(table_data))

	if plot:
		fig = px.line(data, x = 'Date', y = plot_y, log_y = True)
		fig.show()
		fig.write_html('index.html')

run(
	ticker = '^GSPC',
	leverage_levels=[1.25, 1.5, 2, 3],
	#period = ['2000-01-01', '2022-12-31'],
)
