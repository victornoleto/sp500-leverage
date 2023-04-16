import pandas as pd
import plotly.express as px

expense_ratio = 1
daily_expense_ratio = 1/365 # approximately

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

			daily_profit = leverage_value - last_leverage_value

			# I am not sure if the ER calculation is correct
			if daily_profit > 0:
				leverage_value = leverage_value - (daily_profit * daily_expense_ratio)

			# Just to avoid values like 0.00001
			if leverage_value < 0.1:
				leverage_value = 0

		leverage_data.append(leverage_value)

		last_value = value

	return leverage_data

sp500 = pd.read_csv('SPX.csv')

close_values = sp500['Close']

sp500['Leverage_1.25x'] = calculate_leverage(close_values, 1.25)
sp500['Leverage_1.5x'] = calculate_leverage(close_values, 1.5)
sp500['Leverage_2x'] = calculate_leverage(close_values, 2)
sp500['Leverage_3x'] = calculate_leverage(close_values, 3)
sp500['Leverage_5x'] = calculate_leverage(close_values, 5)

fig = px.line(
	sp500,
	x='Date',
	y=['Close', 'Leverage_1.25x', 'Leverage_1.5x', 'Leverage_2x', 'Leverage_3x', 'Leverage_5x'],
	log_y=True
)

fig.show()
fig.write_html('index.html')