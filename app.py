import pandas as pd
import plotly.express as px
import yfinance as yf
import numpy as np
from tabulate import tabulate
import statistics
import math
import os, json, hashlib

expense_ratio = 1/100
daily_expense_ratio = expense_ratio/365 # approximately

def get_data(ticker, period):

	args = {
		'tickers': ticker,
		'interval': '1d',
		'progress': False
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

		print('Downloading data...')

		df = yf.download(**args)

		# Save to CSV
		df.to_csv(filename)

		df['Date'] = df.index

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

def max_drawdown(values):
    
	mdd = 0

	peak = values[0]
    
	for x in values:
        
		if x > peak: 
			peak = x
        
		dd = (peak - x) / peak
        
		if dd > mdd:
			mdd = dd

	return round(mdd * 100, 3)

def standart_deviation(values):

	tmp = []

	for index, value in enumerate(values):

		if index == 0:
			continue

		tmp.append((value/values[index-1]) - 1)

	stdev = statistics.stdev(tmp) * 16

	return round(stdev * 100, 3)

def cagr(values):

	l = len(values)

	years = math.floor(l / 365)

	appreciation = values[l-1] / values[0]

	cagr = pow(appreciation, 1/years) - 1

	return round(cagr * 100, 3)

def run(ticker, leverage_levels, period = 'max', plot = False):

	data = get_data(ticker, period)

	close_values = data['Close']

	last_close = close_values.iloc[-1]

	min_date = data['Date'].iloc[0]
	max_date = data['Date'].iloc[-1]

	table_data = [
		['#', 'No Leveraged'],
		['End Value (US$)', last_close],
		['Appreciation (%)', '-'],
		['Stdev (%)', standart_deviation(close_values)],
		['Max. Drawdown (%)', max_drawdown(close_values)],
		['CAGR (%)', cagr(close_values)],
	]

	plot_y = ['Close']
	
	for level in leverage_levels:

		c = 'Leverage_' + str(level) + 'x'

		leveraged_data = calculate_leverage(data['Close'], level)
		leveraged_last_close = round(leveraged_data[-1], 3)
		leveraged_appreciation = round(((leveraged_last_close / last_close) - 1) * 100, 3)
		stdev = standart_deviation(leveraged_data)

		table_data[0].append(c)
		table_data[1].append(leveraged_last_close)
		table_data[2].append(leveraged_appreciation)
		table_data[3].append(stdev)
		table_data[4].append(max_drawdown(leveraged_data))
		table_data[5].append(cagr(leveraged_data))

		data[c] = leveraged_data

		plot_y.append(c)

	print(ticker, ':', min_date, 'to', max_date)
	print(tabulate(table_data))

	if plot:
		fig = px.line(data, x = 'Date', y = plot_y, log_y = True)
		fig.show()
		fig.write_html('index.html')

run(
	ticker = '^GSPC',
	leverage_levels=[1.5, 2, 3],
	#period = ['1980-01-01', '2022-12-31'],
	period = 'max',
	plot = True
)
