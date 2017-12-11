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
        for market in markets:
            try:
                res = requests.get(market['api']).json()
                price = res[market['last_price_key']]
                ticker = {
                    'date': datetime.datetime.utcnow(),
                    'price': float(price)
                }

                db[market['name']].insert_one(ticker)
            except:
                continue
        time.sleep(config['sampling_time'])
