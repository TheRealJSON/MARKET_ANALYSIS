from os import error
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

candlestick_patterns = {}

def read_candlestick_patterns_from_JSON(configFilePath):
    configFile = open(configFilePath)
    pattern_config_parser = JSONLogicParser()
    
    data = json.load(configFile)

    for candle_pattern in data['patterns']:
        #print('current pattern: ' + candle_pattern) # current pattern
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

def classify_bullish_pinbar(candlesticks):
    first_candle = candlesticks['first_candle']
    second_candle = candlesticks['second_candle']
    third_candle = candlesticks['third_candle']

    is_small_body = second_candle['realbody'] <= (second_candle['range']/3)

    is_body_in_upper_half = min(second_candle['Open'], second_candle['Price']) > (second_candle['High'] + second_candle['Low']) / 2

    is_bullish_pinbar = is_small_body and is_body_in_upper_half                 \
                        and (second_candle['Price'] < first_candle['Price'])    \
                        and (second_candle['Price'] < third_candle['Price'])    \
                        and (second_candle['Price'] < first_candle['Open'])     \
                        and (second_candle['Open'] < third_candle['Price']) # make sure third candle dominates upward after pin

    return is_bullish_pinbar



read_candlestick_patterns_from_JSON('C:/Users/Jaso/Documents/Stock Market/candlestick_patterns.json')

dataFrame = pd.read_csv('C:/Users/Jaso/Documents/Stock Market/Bitcoin Historical Data.csv') # Returns a DataFrame, 2D data structure
dataFrame.reset_index(drop=True) #needed for comparison of rows for some strange reason

# Check row count is divisible by 3 for processing 3 candles a time
remainder_row_count = len(dataFrame) % 3
for x in range(remainder_row_count):
    dataFrame = dataFrame.drop(x)

# Make copy of DataFrame for editing (should not edit structures being iterated over)
dataFrameCopy = dataFrame.copy()
dataFrameCopy['realbody'] = ""#pd.series(dtype="float64")""
dataFrameCopy['range'] =  ""#pd.series(dtype="float64")

# Loop over candlesticks and identify patterns
candle_names = ta.get_function_groups()['Pattern Recognition']

# Set pre-condition columns/attributes
for index, row in dataFrame.iterrows(): 
    #print(np(row['Open'], dtype=float))
    dataFrameCopy.at[index, 'realbody'] = row['Open'] - row['Price']
    dataFrameCopy.at[index, 'range'] = row['High'] - row['Low']


for index, row in dataFrame.iterrows():
    # index starts at 1, decrement each one to prevent IndexError at last index
    # TODO: fix, but cmon not got time for this bs now
    index = index - 1

    if index < 3:
        index = 3 #inefficient quickfix to bullshit

    # dictionary used for dynamic var references
    candlestick_frame = {} # can be confused with DataFrame..rename?
    candlestick_frame['first_candle']   = dataFrameCopy.iloc[index - 2,:]
    candlestick_frame['second_candle']  = dataFrameCopy.iloc[index - 1,:]
    candlestick_frame['third_candle']   = dataFrameCopy.iloc[index,:]

    # loop over candlestick patterns and check if any are present
    for key, candle_pattern in candlestick_patterns.items():
        dataFrameCopy.at[index+1, 'bullish_pinbar'] = candle_pattern.check_candlesticks_match_pattern(candlestick_frame)

    # TODO: FOR SOME REASON. NEED TO USE index+1..one is 0 based on is not? iloc is diff to .at??
    #dataFrameCopy.at[index+1, 'bullish_swing'] = classify_bullish_swing(candlestick_frame)
    #dataFrameCopy.at[index+1, 'bullish_pinbar'] = classify_bullish_pinbar(candlestick_frame)

dataFrameCopy.to_csv("C:/Users/Jaso/Documents/Stock Market/out.csv")

# Plot results on graph
"""
trace = go.Candlestick(
            open=dataFrameCopy['Open'],
            high=dataFrameCopy['High'],
            low=dataFrameCopy['Low'],
            close=dataFrameCopy['Price'],
            text=dataFrameCopy['Price'],
            hoverinfo='text'
            )
data = [trace]
"""


trace = go.Candlestick(
            open=dataFrameCopy['Open'],
            high=dataFrameCopy['High'],
            low=dataFrameCopy['Low'],
            close=dataFrameCopy['Price'],
            text=dataFrameCopy['bullish_pinbar'],
            hoverinfo='text'
            )
data = [trace]

plot(data, filename='C:/Users/Jaso/Documents/Stock Market/go_candle1.html')
