#! /usr/bin/env python3

import json
import requests
import time

from client import FairlayPythonClient

# Some pre-defined market filters
class FILTER(object):
    NFL = {'Cat': 13, 'Comp': 'NFL'}
    NCAAF = {'Cat': 13, 'Comp': 'NCAA'}
    NBA = {'Cat': 12, 'Comp': 'NBA'}


def fetch_large_market_orders(min_mBTC_amount, market_filter={}):
    client = FairlayPythonClient()

    print(f'Fetching markets and odds {market_filter} ...')
    from_id = 0
    increment = 10000

    new_markets = []
    # filters = {'FromID': from_id,'NoZombie': True, "OnlyActive": True, "SortPopular": True}
    # filters.update(market_filter)
    # new_markets = client.get_markets_and_odds(filters)
    while True:
        filters = {'FromID': from_id, 'ToID': from_id + increment,
                   'NoZombie': True, "OnlyActive": True,
                   "SortPopular": True}
        filters.update(market_filter)
        mkts = client.get_markets_and_odds(filters)

        if mkts is not None:
            new_markets += mkts

        if len(new_markets) < from_id + increment:
            break
        else:
            from_id += increment
        print('...')

    print(f'Filtering market orders >= {min_mBTC_amount} mBTC ...')
    count = 0
    for market in new_markets:
        if market['OrdBStr']:
            OrderBook = [json.loads(ob) for ob in market['OrdBStr'].split('~') if ob]
        large_order = []
        for ru_order in OrderBook:
            # Array of open bids orders
            for order in ru_order['Bids']:
                # order: [ price, amount ]
                #   price: the decimal odds at which the order is placed.
                #   amount: the amount in mBTC.
                if order[1] >= min_mBTC_amount:
                    large_order.append(order)
            # Array of open asks orders
            for order in ru_order['Asks']:
                if order[1] >= min_mBTC_amount:
                    large_order.append(order)

        # No large order for this market, skip printing
        if len(large_order) == 0:
            continue

        count += 1
        # Many fields that can be displayed
        MarketCategory = client.MARKET_CATEGORY[market['CatID']]
        MarketType = client.MARKET_TYPE[market['_Type']]
        MarketPeriod = client.MARKET_PERIOD[market['_Period']]
        SettlementType = client.MARKET_SETTLEMENT[market['SettlT']]
        # Visit https://fairlay.com/market/{market['ID']} on browser
        print(f"MarketID:{market['ID']} Category:{MarketCategory} Comp:{market['Comp']} Period:{MarketPeriod} large_order([odds, amount]):{large_order}")
    print(f'({count}/{len(new_markets)} row(s) in total)')

def usd_to_mBTC(dollar):
    try:
        # https://www.blockchain.com/api/exchange_rates_api
        call = 'https://blockchain.info/tobtc?currency=USD&value=' + str(dollar)
        response = requests.get(call)
        if response.status_code != 200:
            print('Cannot get recent USD/BTC exchange rate.')
            return 100
        btc = response.json()
        return btc * 1000
    except requests.exceptions.ConnectionError:
        print('Cannot get recent USD/BTC exchange rate.')
        return 100

if __name__ == '__main__':
    min_usd_amount = 5000
    min_mBTC_amount = usd_to_mBTC(min_usd_amount)
    fetch_large_market_orders(min_mBTC_amount, FILTER.NFL)
    fetch_large_market_orders(min_mBTC_amount, FILTER.NCAAF)
    fetch_large_market_orders(min_mBTC_amount, FILTER.NBA)
    # fetch_large_market_orders(min_mBTC_amount) # All
