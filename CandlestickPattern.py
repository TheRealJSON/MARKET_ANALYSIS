import re

class CandlestickPattern:

    def __init__(self, name, candle_count, rules) -> None:
        self.pattern_name = name
        self.candle_count = candle_count
        self.rules_expression = rules


    def check_candlesticks_match_pattern(self, candlesticks):
        # replace placeholders inside expression string with runtime values
        runtime_rules_expression = self.rules_expression

        placeholder_regex = '[_a-zA-Z]+\.[_a-zA-Z]+' # i.e. second_candle.length
        placeholder_candle_regex = '[_a-zA-Z]+\.'
        placeholder_property_regex = '\.[_a-zA-Z]+'

        candlestick_property_placeholders = re.findall(placeholder_regex, self.rules_expression)
        
        for property_placeholder in candlestick_property_placeholders:
            candlestick_identifier = re.search(placeholder_candle_regex, property_placeholder).group(0).replace('.', '')
            property_identifier = re.search(placeholder_property_regex, property_placeholder).group(0).replace('.', '')

            runtime_value = str(candlesticks[candlestick_identifier][property_identifier])

            runtime_rules_expression = runtime_rules_expression.replace(property_placeholder, runtime_value)
        
        print (runtime_rules_expression)
        if eval(runtime_rules_expression): 
            print('PATTERN MATCH')
        
        return eval(runtime_rules_expression) #TODO: NEED TO VALIDATE the expression before dangerous eval()


        



      


                     
  

                    


                    
                        

