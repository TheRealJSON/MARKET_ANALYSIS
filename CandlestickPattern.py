import re
from JSONLogicParser import JSONLogicParser

class CandlestickPattern:

    def __init__(self, name, candle_count, rules) -> None:
        self.pattern_name = name
        self.candle_count = candle_count 
        self.rules_expression = rules


    def check_candlesticks_match_pattern(self, candlesticks):
        runtime_rules_expression = JSONLogicParser.replaceStringPlaceholdersWithValues(self.rules_expression, candlesticks)
        print(self.rules_expression)
        return eval(runtime_rules_expression) #TODO: NEED TO VALIDATE the expression before dangerous eval()