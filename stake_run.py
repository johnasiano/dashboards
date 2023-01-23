#! /usr/bin/env python3

import argparse
import threading
import time

from client import StakePythonClient

class StakeBetFetcher(object):
    def __init__(self, min_usd_amount=0, fetch_interval=60):
        self.min_usd_amount = min_usd_amount
        self.fetch_interval = fetch_interval # in seconds
        self.last_bets = set()
        self.client = StakePythonClient()
        self.event = threading.Event()
        threading.Thread(target=self.__run).start()
        print(f'Fetching bets >= ${self.min_usd_amount}'
              f' in every {self.fetch_interval} seconds.'
              ' Press Ctrl-C to terminate the program.\n')

    def __run(self):
        while not self.event.is_set():
            self.fetch_new_markets()
            self.event.wait(self.fetch_interval)

    def fetch_new_markets(self):
        # Get real time currency conversion rate
        to_usd_rates = self.client.get_usd_currency_conversion_rate()

        if self.min_usd_amount < 1000:
            # fetch_interval should be smaller e.g. < 1 minute
            sport_bets = self.client.get_all_sport_bets(50)
        else:
            # fetch_interval can be larger e.g. > 1 minute
            sport_bets = self.client.get_highroller_sport_bets(50)

        # Parse bets
        new_bets = set()
        for bet in sport_bets:
            iid = bet["iid"]
            new_bets.add(iid)
            if iid in self.last_bets:
                continue

            # Can filter by these if needed
            active = bet["bet"]["active"]  # bool type
            status = bet["bet"]["status"]  # confirmed|settled|cashout|...
            # createdAt = bet["bet"]["createdAt"]
            # updatedAt = bet["bet"]["updatedAt"]

            amount = bet["bet"]["amount"]
            currency = bet["bet"]["currency"]
            usd_amount = amount * to_usd_rates[currency]
            if usd_amount < self.min_usd_amount:
                continue

            ### Single bet / Multibet
            # Multibet if outcome_list has more than 1 element, otherwise single bet
            # Multibet may contain sub-bets for different competitions/sports.
            #
            # How to calculate the "Total odds" for a multibet?
            # Looks like it is not the sum of each sub-bets odds.
            # E.g. https://stake.com/?modal=bet&iid=sport:15691453
            outcome_list = bet["bet"].get("outcomes")
            if not outcome_list:
                continue
            bet_odds = []
            for outcome in outcome_list:
                sport = outcome["fixture"]["tournament"]["category"]["sport"]["slug"]
                # if sport not in ('american-football', 'basketball'):
                #     bet_odds = []
                #     break
                bet_odds.append({
                    "odds": outcome["odds"],
                    "competitors": outcome["fixture"]["name"],
                    "tournament": outcome["fixture"]["tournament"].get("name"),
                    "sport_category": outcome["fixture"]["tournament"]["category"].get("name"),
                    "sport": sport
                })
            if not bet_odds:
                continue

            # Display bet info
            is_multibet = "Multibet" if len(outcome_list) > 1 else "Single bet"
            print(f"betID:'{iid}'  active:{active}  Status:{status}  Amount:${usd_amount:.2f}  {is_multibet}:{bet_odds}")
            # print(bet)
        self.last_bets = new_bets

    def stop(self):
        self.event.set()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch Stake.com bets in real time')
    parser.add_argument('-m', '--min_usd_amount', type=float, required=False, default=1000,
                        help='The minimum USD amount for bets to fetch (default:1000)')
    parser.add_argument('-i', '--interval', type=int, required=False, default=60,
                        help='Fetch interval in seconds (default:60)')
    args = parser.parse_args()

    fetcher = StakeBetFetcher(min_usd_amount=args.min_usd_amount,
                                 fetch_interval=args.interval)

    # Ctrl-C to terminate the program
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            fetcher.stop()
            break
