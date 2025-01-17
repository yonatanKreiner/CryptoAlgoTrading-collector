import json
import traceback

import requests
import time
import datetime
import pymongo

config = json.load(open('src/watcher_config.json'))
markets = config['markets']
client = pymongo.MongoClient('MONGO_PATH')


def watch_markets():
    while True:
        sample_time = datetime.datetime.utcnow()
        tickers = {}

        for market in markets:
            try:
                res = requests.get(market['api'], proxies=config['proxies'], timeout=10)
                json_res = res.json()
                price = json_res[market['last_price_key']]
                volume = json_res[market['24_hours_volume_key']]
                bid = json_res[market['bid_key']]
                ask = json_res[market['ask_key']]
                ticker = {
                    'date': sample_time,
                    'price': float(price),
                    'volume': float(volume),
                    'bid': float(bid),
                    'ask': float(ask)
                }
                tickers[market['name']] = ticker
            except json.JSONDecodeError as e:
                with open('error.log', 'a+') as log:
                    log.write(str(datetime.datetime.utcnow()) + '\n' + str(res) + '\n')
            except Exception as e:
                with open('error.log', 'a+') as log:
                    log.write(str(datetime.datetime.utcnow()) + ' ' + str(e) + '\n' + traceback.format_exc() + '\n')

        if len(tickers) == len(markets):
            for market in markets:
                market_name = market['name']
                for i in range(5):
                    try:
                        client.bitteamdb[market_name].insert_one(tickers[market_name])
                        break
                    except pymongo.errors.AutoReconnect:
                        with open('error.log', 'a+') as log:
                            log.write(str(datetime.datetime.utcnow()) + ' AutoReconnect' + '\n')

                        time.sleep(pow(2, i))
                    except Exception as ex:
                        with open('error.log', 'a+') as log:
                            log.write(str(datetime.datetime.utcnow()) + ' ' + str(ex) + '\n')

        time.sleep(config['sampling_time'])
