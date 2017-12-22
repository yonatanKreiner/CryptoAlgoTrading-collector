import json
import traceback

import requests
import time
import datetime
from pymongo import MongoClient

config = json.load(open('src/watcher_config.json'))
markets = config['markets']
client = MongoClient('mongodb://ariel:ariel@ds127536.mlab.com:27536/collector')
db = client.collector


def watch_markets():
    while True:
        sample_time = datetime.datetime.utcnow()
        tickers = {}

        for market in markets:
            try:
                res = requests.get(market['api']).json()
                price = res[market['last_price_key']]
                volume = res[market['24_hours_volume_key']]
                bid = res[market['bid_key']]
                ask = res[market['ask_key']]
                ticker = {
                    'date': sample_time,
                    'price': float(price),
                    'volume': float(volume),
                    'bid': float(bid),
                    'ask': float(ask)
                }
                tickers[market['name']] = ticker

            except Exception as e:
                with open('error.log', 'a+') as log:
                    log.write(str(e) + '\n' + traceback.format_exc() + '\n')

        if len(tickers) == len(markets):
            for market in markets:
                market_name = market['name']
                db[market_name].insert_one(tickers[market_name])

        time.sleep(config['sampling_time'])
