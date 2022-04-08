from os import error
from sre_constants import SUCCESS
import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
from plotly.offline import plot
import plotly.graph_objs as go
#import scipy.stats as stats
#import seaborn as sns
#from matplotlib import rcParams

import talib as ta

#from JSONParser import read_candlestick_patterns_from_JSON
import json

from JSONLogicParser import JSONLogicParser
from CandlestickPattern import CandlestickPattern
import re

global candlestick_patterns
candlestick_patterns = {}
global candlestick_data 
candlestick_data = {}


def read_candlestick_patterns_from_JSON(configFilePath):
    configFile = open(configFilePath)
    pattern_config_parser = JSONLogicParser()
    
    data = json.load(configFile)

    for candle_pattern in data['patterns']:
        pattern_candle_count = data['patterns'][candle_pattern]['candle_count']
        pattern_rules_tree = data['patterns'][candle_pattern]['rules']

        pattern_rules_string = pattern_config_parser.convertJSONExpressionTreeToString(pattern_rules_tree)
         
        candlestick_patterns[candle_pattern] = CandlestickPattern(candle_pattern, pattern_candle_count, pattern_rules_string)

    configFile.close()


def classify_bullish_swing(first_candle, second_candle, third_candle):
    first_candle_low = first_candle['Low']
    second_candle_low = second_candle['Low']
    third_candle_low = third_candle['Low']

    is_bullish_swing = first_candle_low > second_candle_low and second_candle_low < third_candle_low

    return is_bullish_swing

def load_candlestick_patterns():
    success = False

    # Load Candlestick Pattern Definitions
    read_candlestick_patterns_from_JSON('/Users/jasondejonge/Documents/Software Engineering/Market_Analysis/MARKET_ANALYSIS/candlestick_patterns.json')

    success = True #TODO: fix up over-engineered success flag system by adding error handling etc.

    return success

def load_candlestick_data():
    success = False

    # Load Candlestick Pattern Definitions
    global candlestick_data
    candlestick_data = pd.read_csv('/Users/jasondejonge/Documents/Software Engineering/Market_Analysis/MARKET_ANALYSIS/Bitcoin Historical Data.csv') # Returns a candlestick_data, 2D data structure
    candlestick_data.reset_index(drop=True) #needed for comparison of rows for some strange reason

    success = True #TODO: fix up over-engineered success flag system by adding error handling etc.

    return success

def load_derived_attributes():
    success = False
    global candlestick_data
    
    candlestick_dataCopy = candlestick_data.copy() # Don't edit collection being iterated over

    # Set pre-condition columns/attributes
    for index, row in candlestick_data.iterrows(): 
        candlestick_dataCopy.at[index, 'realbody'] = row['Open'] - row['Price']
        candlestick_dataCopy.at[index, 'range'] = row['High'] - row['Low']
    
    # Finalise
    candlestick_data = candlestick_dataCopy

    success = True

    return success

def bootstrap():
    bootstrap_success = False

    # ==================================
    # Load Candlestick Pattern Definitions
    # ==================================
    bootstrap_success = load_candlestick_patterns()

    # ==================================
    # Load Candlestick Price Data
    # ==================================
    bootstrap_success = load_candlestick_data()

    # ==================================
    # Load Derived Price Data Attributes
    # ==================================
    bootstrap_success = load_derived_attributes()

    return bootstrap_success


    



bootstrap_success = bootstrap()

if (bootstrap_success):

    candlestick_dataCopy = candlestick_data.copy()

    for index, row in candlestick_data.iterrows():
        # index starts at 1, decrement each one to prevent IndexError at last index
        # TODO: fix, but cmon not got time for this bs now
        index = index - 1

        if index < 3:
            index = 3 #inefficient quickfix to bullshit

        # dictionary used for dynamic var references
        candlestick_frame = {} # can be confused with candlestick_data..rename?
        candlestick_frame['first_candle']   = candlestick_dataCopy.iloc[index - 2,:]
        candlestick_frame['second_candle']  = candlestick_dataCopy.iloc[index - 1,:]
        candlestick_frame['third_candle']   = candlestick_dataCopy.iloc[index,:]

        # loop over candlestick patterns and check if any are present
        for key, candle_pattern in candlestick_patterns.items():
            candlestick_dataCopy.at[index, candle_pattern.pattern_name] = candle_pattern.check_candlesticks_match_pattern(candlestick_frame)

    candlestick_data = candlestick_dataCopy

    # Plot results on graph
    trace = go.Candlestick(
                open=candlestick_dataCopy['Open'],
                high=candlestick_dataCopy['High'],
                low=candlestick_dataCopy['Low'],
                close=candlestick_dataCopy['Price'],
                text=candlestick_dataCopy['bullish_pinbar'],
                hoverinfo='text'
                )
    data = [trace]

    plot(data, filename='/Users/jasondejonge/Documents/Software Engineering/Market_Analysis/MARKET_ANALYSIS/go_candle1.html')

    # ====================================================
    # Calculate predictive success of candlestick patterns
    # ====================================================
    correct_count = 0
    incorrect_count = 0
    success_criteria = 'third_candle.Price > first_candle.Price'
    runtime_success_criteria = success_criteria

    for index, row in candlestick_data.iterrows():
        index = index - 1
        
        if index >= (len(candlestick_data) - 4):
            index = len(candlestick_data) - 5 #inefficient quickfix to bullshit

        # dictionary used for dynamic var references
        candlestick_frame = {} # can be confused with candlestick_data..rename?
        candlestick_frame['first_candle']   = candlestick_dataCopy.iloc[index,:]
        candlestick_frame['second_candle']  = candlestick_dataCopy.iloc[index + 1,:]
        candlestick_frame['third_candle']   = candlestick_dataCopy.iloc[index + 2,:]

        for key, candle_pattern in candlestick_patterns.items():
            if candlestick_frame['first_candle'][candle_pattern.pattern_name] == True: # if then check if flag was successful
                runtime_success_criteria = JSONLogicParser.replaceStringPlaceholdersWithValues(success_criteria, candlestick_frame)
                successful_guess = eval(runtime_success_criteria)
                candlestick_dataCopy.at[index, (candle_pattern.pattern_name + '_success')] = successful_guess


        
    candlestick_dataCopy.to_csv("/Users/jasondejonge/Documents/Software Engineering/Market_Analysis/MARKET_ANALYSIS/out.csv")

