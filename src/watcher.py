import os
import json
import requests
import time

config = json.load(open('src/watcher_config.json'))
markets_prices = {}
markets = config['markets']
sampling_time = 0


def initialize_markets_prices_list():
    for market in markets:
        markets_prices[market['name']] = []


def watch_markets():
    os.makedirs('output', exist_ok=True)
    initialize_markets_prices_list()
    counter = 0

    while True:
        request_time = time.time()
        
        for market in markets:
            try:
                res = requests.get(market['api']).json()
                price = res[market['last_price_key']]
                data = {
                    'time': request_time,
                    'price': float(price)
                }
                markets_prices[market['name']].append(data)
            except:
                continue
        time.sleep(config['sampling_time'])
        counter += 1
        sampling_time_minutes = config['sampling_time'] / 60

        if config['file_update_time'] == sampling_time_minutes * counter:
            update_file()
            counter = 0


def update_file():
    for market_name in markets_prices.keys():
        with open('output/' + market_name + '.json', 'w') as file:
            json.dump(markets_prices[market_name], file)
