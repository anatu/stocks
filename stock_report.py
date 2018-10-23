# Develop and serve via email a report of analyzed stock data with buy-sell recommendations
# See e.g. https://ntguardian.wordpress.com/2016/09/19/introduction-stock-market-data-python-1/ 
# MAJOR INDICATORS: http://www.investopedia.com/articles/active-trading/041814/four-most-commonlyused-indicators-trend-trading.asp

import os
import pandas as pd
import pandas_datareader as pdr # Pandas submodule for getting data returned as df objects
import datetime
import matplotlib.pyplot as plt
import analysis_funcs as funcs
import time

from string import Template
# See https://github.com/kootenpv/yagmail#no-more-password-and-username for yagmail reference\
# and https://kootenpv.github.io/2016-04-24-yagmail for use cases (incl. sending attachment)
import yagmail

# %matplotlib inline
# %pylab inline


class Stock_Analyze():

    def __init__(self):
        self.basepath = "C:/Users/natu.anand/Documents/Magic Briefcase/stocks"
        listnames = [
        "test_companylist.csv",
        # "nasdaq_companylist.csv", 
        # "nyse_companylist.csv", 
        # "amex_companylist.csv"
        ]
        
        self.stock_info = pd.concat(pd.read_csv(f) for f in listnames)


    def generate_report(self):
        # TOPLINE Function that generates the report. All other 
        # methods should be called within this one so that the main function
        # only has to call this when the class is instantiated.

        # industries = ["Basic Industries", "Consumer Non-Durables"]
        industries = ["Finance", "Technology"]

        ############################
        # TODO: Get a list of clients to exclude  
        # confidentiality and/or non-compete compliance purposes
        excluded_clients = []
        ############################


        industry_df = self.stock_info[self.stock_info["Sector"].isin(industries) == True]
        self.stocklist = industry_df["Symbol"].values.tolist()

        if len(self.stocklist) == 0:
            raise ValueError("No stock information detected in input CSV file. Please check original data source.")


        
        delta = datetime.timedelta(days = 100)
        end = datetime.date.today()
        start = end - delta

        self.report_data = pd.DataFrame()

        timer_start = time.time()

        for stock in self.stocklist:

            try:
                worker = pdr.get_data_yahoo(stock, start, end)
            except pdr._utils.RemoteDataError:
                print("Error in downloading data for " + stock + ". Continuing to the next stock...")
                continue

            worker["Symbol"] = stock

            ################################################
            # Calculate relevant moving averages and regimes
            ################################################
            worker["Regime"] = funcs.compute_mav_regime(short_interval = 20, long_interval = 50, data = worker)
            # worker = compute_mav_regime(short_interval = 20, long_interval = 50, data = worker)

            # Calculate OBV
            worker["OBV"] = funcs.compute_obv(data = worker)

            # Calculate MACD crossover
            worker["MACD"] = funcs.compute_macd(data = worker)

            ################################################
            # Calculate RSI
            # TODO: Implement in analysis_funcs then use here
            ################################################

            self.report_data = pd.concat([self.report_data, worker])
            
            timer_end = time.time()
            print(str(timer_end - timer_start) + " seconds elapsed")


        self.recommendations = self.interpret_report()
        self.serve_results(recos = self.recommendations)

        return None

  
    def interpret_report(self):
        ##################################
        # TODO: Write a method that accepts the report with all of the computed
        # values, then runs analysis on it to generate recommendations which  
        # can be passed into serve_results and incorporated directly 
        # into the body of the email that's sent out (e.g. buy this stock, sell this stock, etc.)
        ##################################

        # Initialize a dataframe that will store information for stocks
        # that we recommend to purchase 
        recommendations = pd.DataFrame()

        self.report_data = self.report_data.reset_index()
        syms = self.report_data["Symbol"].drop_duplicates().values.tolist()
        print(syms)

        for sym in syms:


            # FIRST, Analyze the MAV trends to figure out if the stock movement is bullish
            # Slice out all the dates on which the MAV crosses over from negative to positive
            mav_crosses = self.report_data.loc[(self.report_data["Symbol"] == sym) \
            & (self.report_data["Regime"].shift(1) == -1) & (self.report_data["Regime"] == 1)]

            # Pull out the news
            if len(mav_crosses) > 0:
                latest_turnaround = str(mav_crosses["Date"].max())
            else:
                latest_turnaround = "No MAV crossover"
            

            # SECOND, look at the OBV to figure out how it is performing relative to stock price
            obv_differential = self.report_data.loc[(self.report_data["Symbol"] == sym) \
            & (self.report_data["OBV"] > self.report_data["OBV"].shift(-3))].sort_values(by = ["Date"])


            # Interpret the MACD to determine crossovers of MACD vs signal and MACD vs zero
            ##############################
            ##############################
            # TODO: IMPLEMENT THIS
            ##############################
            ##############################

            # Finally append the cut-down matrix to the recommendations list
            # recommendations = recommendations.append(finaldf)

        # TODO: Change this return type to be the final output
        # (either in HTML or CSV Form, preferably as an HTML document)
        return None


    def get_email_contacts(self, filename):
        contacts = []
        with open(filename, 'r', encoding = 'utf-8') as contacts_file:
            for contact in contacts_file:
                contacts.append([contact.split()[0], contact.split()[1]])
        return contacts


    def serve_results(self, recos):
        contacts = self.get_email_contacts(filename = "email_recipients.txt")
        # The password credentials for this address are stored on my local keyring
        yag = yagmail.SMTP('layedest@gmail.com')

        # Save the report CSV to a temporary location so it can be passed into email attachment
        outpath = os.path.join(self.basepath, "outputs", "report - %s.csv" % (str(datetime.datetime.today())))

        recos.to_csv(outpath)

        for contact in contacts:
            subj_text = "%s's stock report - %s" % (contact[0], datetime.datetime.today())

            ######################################
            # TODO: Pass the interpretation into here as the body of the email 
            # using the "contents" parameter (needs to be raw HTML string)
            yag.send(to=contact[1], subject = subj_text, attachments = outpath)
            ######################################

        
if __name__ == "__main__":
    global_start = time.time()
    analyzer = Stock_Analyze()
    
    analyzer.generate_report()

        
    global_end = time.time()
    print("COMPLETE! Total elapsed runtime is " + str(global_end - global_start) + " seconds")


################################################3



