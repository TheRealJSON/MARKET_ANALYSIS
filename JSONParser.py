import json

def read_candlestick_patterns_from_JSON(configFilePath):
    configFile = open(configFilePath)
    
    data = json.load(configFile)

    for i in data['patterns'] :
        # read each rule into an array/list




