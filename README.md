# dashboards

# FairlayAPI
Requirements: Python 3 installed

`run.py` program can display: All of the large open orders (over $5000) placed in those 3 markets: American football / NFL, college football / NCAAF, and basketball / NBA. Currently, the threshold `$5000`, the markets type, and displayed fields are hard-coded.

The currency used by Fairlay is mBTC, this program gets the USD/BTC exchange rate from [Blockchain](https://www.blockchain.com/api/exchange_rates_api) API and convert the threshold `$5000` to mBTC value.

Run the program:
```bash
$ python run.py
Or
$ ./run.py
```
# Stake.com
Tasks with Stake APIs

Requirements: Python 3 installed
```
$ pip install -r requirements.txt
```
Tested with Python 3.7.

If you have registered on the website, you can access https://stake.com/settings/api and get a token. This is not required by the client if you are requesting public information. Otherwise, you can setup an environment variable `export STAKE_API_TOKEN=xxxxx`, and then the client will use this token for API requests.

Run the program:
```
$ python run.py --help
usage: run.py [-h] [-m MIN_USD_AMOUNT] [-i INTERVAL]

Fetch Stake.com bets in real time

optional arguments:
  -h, --help            show this help message and exit
  -m MIN_USD_AMOUNT, --min_usd_amount MIN_USD_AMOUNT
                        The minimum USD amount for bets to fetch
                        (default:1000)
  -i INTERVAL, --interval INTERVAL
                        Fetch interval in seconds (default:60)


$ ./run.py -m 1500 -i 10
Fetching bets >= $1500.0 in every 10 seconds. Press Ctrl-C to terminate the program.

betID:'sport:15696289'  active:True  Status:confirmed  Amount:$6453.23  Single bet:[{'odds': 1.73, 'competitors': 'Green Bay Packers - Detroit Lions', 'tournament': 'NFL', 'sport_category': 'USA', 'sport': 'american-football'}]
betID:'sport:15697423'  active:True  Status:confirmed  Amount:$1818.59  Multibet:[{'odds': 1.7, 'competitors': 'Sonego, Lorenzo - Fucsovics, Marton', 'tournament': 'ATP Metz, France Men Singles', 'sport_category': 'ATP', 'sport': 'tennis'}, {'odds': 1.14, 'competitors': 'Verdasco, Fernando - Kecmanovic, Miomir', 'tournament': 'ATP Nur-Sultan, Kazakhstan Men Singles', 'sport_category': 'ATP', 'sport': 'tennis'}, {'odds': 1.35, 'competitors': 'Novak, Dennis - Bachinger, Matthias', 'tournament': 'ATP Challenger, Biel, Switzerland Men Singles', 'sport_category': 'Challenger', 'sport': 'tennis'}]
...
(Ctrl-C)
```
To view a bet on browser, visit `https://stake.com/?modal=bet&iid={betID}`. Notice there are **multibet**, e.g. https://stake.com/?modal=bet&iid=sport:15697423.


More details about the design: https://github.com/sitingren/SportsOrderbook/discussions/2
