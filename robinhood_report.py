from Robinhood import Robinhood
import csv
import os
from get_symboldata import Stock_Analyze


class RobinhoodReport():

	def __init__(self):
		#Setup
		my_trader = Robinhood();
		#login
		my_trader.login(username="username", password="password")


	def choose_trades(self):
		chooser = Stock_Analyze()
		
		# TODO: This needs to be a list of stock symbols that are potential buys
		recs = Stock_Analyze.tech_report()



		# TODO: Refactor to make the trades
		# stock_instruments = []
		# for rec in recs:		
		# 	stock_instruments.append(my_trader.instruments("GEVO")[0])

		# #Get a stock's quote
		# my_trader.print_quote("AAPL")

		# #Prompt for a symbol
		# my_trader.print_quote();

		# #Print multiple symbols
		# my_trader.print_quotes(stocks=["BBRY", "FB", "MSFT"])

		# #View all data for a given stock ie. Ask price and size, bid price and size, previous close, adjusted previous close, etc.
		# quote_info = my_trader.quote_data("GEVO")
		# print(quote_info);

		# #Place a buy order (uses market bid price)
		# buy_order = my_trader.place_buy_order(stock_instrument, 1)

		# #Place a sell order
		# sell_order = my_trader.place_sell_order(stock_instrument, 1)


if __name__ == "__main__":
	trader = 




