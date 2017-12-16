import json
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

                db[market['name']].insert_one(ticker)
            except Exception as e:
                error_file = open("error.log", "w")
                error_file.write("Failed on: {0}\n".format(str(e)))
                error_file.close()
        time.sleep(config['sampling_time'])
