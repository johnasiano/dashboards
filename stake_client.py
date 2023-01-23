#! /usr/bin/env python3

from os import environ
import requests

class StakePythonClient(object):
    ENDPOINT = "https://api.stake.com/graphql"
    HEADERS = {
        "content-type": "application/json",
        "Referer": "https://stake.com/",
        "accept": "*/*",
        "Origin": "https://stake.com",
    }

    def __init__(self, accessToken=None):
        # Stake API TOKEN is required by requests for personal account,
        # but seems not required by requests for public info.
        if accessToken is None:
            accessToken = self._load_access_token()
        self.HEADERS["x-access-token"] = accessToken

    def _load_access_token(self):
        """Find the access token in default places"""
        # Find environment variable $STAKE_API_TOKEN
        if 'STAKE_API_TOKEN' in environ:
            return environ['STAKE_API_TOKEN']
        return ''

    def send_graphql_request(self, data):
        try:
            r = requests.post(self.ENDPOINT, json=data, headers=self.HEADERS)

            if r.status_code == 200:
                # print(json.dumps(r.json(), indent=2))
                return r.json()
            else:
                raise Exception(f"Query failed to run with a {r.status_code}.")
        except requests.exceptions.ConnectionError as e:
            print('Cannot send a GraphQL request to Stake.')
            raise e
        # TODO: retry when hit api limit?

    def get_currency_conversion_rate(self):
        request_data = {
            "operationName": "CurrencyConversionRate",
            "variables": {},
            "query": "query CurrencyConversionRate {\n  info {\n    currencies {\n      name\n      value\n      eur: value(fiatCurrency: eur)\n      jpy: value(fiatCurrency: jpy)\n      usd: value(fiatCurrency: usd)\n      cad: value(fiatCurrency: cad)\n      brl: value(fiatCurrency: brl)\n      cny: value(fiatCurrency: cny)\n      idr: value(fiatCurrency: idr)\n      inr: value(fiatCurrency: inr)\n      krw: value(fiatCurrency: krw)\n      php: value(fiatCurrency: php)\n      rub: value(fiatCurrency: rub)\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        result = self.send_graphql_request(request_data)
        if 'errors' in result:
            raise ValueError(f"Failed to request currency conversion rates: {result}")
        return result["data"]["info"]["currencies"]

    def get_usd_currency_conversion_rate(self):
        """
        This is a CUSTOMIZED query.
        Returns a dict
          {'eth': 3155.569580309246, 'btc': 44863.16733961418, ...}
        """
        request_data = {
            "operationName": "UsdCurrencyConversionRate",
            "variables": {},
            "query": "query UsdCurrencyConversionRate {\n  info {\n    currencies {\n      name\n      value\n    }\n  }\n}\n"
        }
        result = self.send_graphql_request(request_data)
        if 'errors' in result:
            raise ValueError(f"Failed to request usd currency conversion rates: {result}")
        return { cur['name']: cur['value'] for cur in result["data"]["info"]["currencies"] }

    def get_currency_value(self, currency="btc"):
        request_data = {
            "operationName": "CurrencyValue",
            "variables": {"currency": currency},
            "query": "query CurrencyValue($currency: CurrencyEnum!) {\n  info {\n    currency(currency: $currency) {\n      value\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        return self.send_graphql_request(request_data)

    def get_live_sport_list(self):
        request_data = {
            "operationName": "liveSportList",
            "variables": {},
            "query": "query liveSportList {\n  sportList(type: live, limit: 50, offset: 0, liveRank: true) {\n    id\n    name\n    slug\n    fixtureCount(type: live)\n    __typename\n  }\n}\n"
        }
        return self.send_graphql_request(request_data)

    def get_upcoming_sport_list(self):
        request_data = {
            "operationName": "SportList",
            "variables": {"type": "upcoming"},
            "query": "query SportList($type: SportSearchEnum!) {\n  sportList(type: $type, limit: 50, offset: 0) {\n    id\n    name\n    slug\n    fixtureCount(type: $type)\n    __typename\n  }\n}\n"
        }
        return self.send_graphql_request(request_data)

    def get_upcoming_fixture_count(self):
        request_data = {
            "operationName": "FixtureCount",
            "variables": {"type": "upcoming"},
            "query":"query FixtureCount($type: SportSearchEnum!) {\n  fixtureCount(type: $type)\n}\n"
        }
        return self.send_graphql_request(request_data)

    def get_highroller_sport_bets(self, limit=40):
        # LIMIT can't be above 50.
        request_data = {
            "operationName": "highrollerSportBets",
            "variables": {"limit": limit},
            # Below is the official query.
            # "query": "query highrollerSportBets($limit: Int!) {\n  highrollerSportBets(limit: $limit) {\n    ...SportRootBet\n    __typename\n  }\n}\n\nfragment SportRootBet on Bet {\n  id\n  iid\n  bet {\n    ... on SportBet {\n      active\n      amount\n      cashoutMultiplier\n      createdAt\n      currency\n      id\n      payout\n      payoutMultiplier\n      potentialMultiplier\n      updatedAt\n      status\n      user {\n        id\n        name\n        __typename\n      }\n      outcomes {\n        odds\n        fixture {\n          name\n          data {\n            ... on SportFixtureDataMatch {\n              startTime\n              competitors {\n                name\n                abbreviation\n                __typename\n              }\n              __typename\n            }\n            ... on SportFixtureDataOutright {\n              name\n              startTime\n              endTime\n              __typename\n            }\n            __typename\n          }\n          tournament {\n            category {\n              sport {\n                slug\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ... on PlayerPropBet {\n      active\n      amount\n      cashoutMultiplier\n      createdAt\n      currency\n      id\n      odds\n      payout\n      payoutMultiplier\n      updatedAt\n      status\n      user {\n        id\n        name\n        __typename\n      }\n      playerProps {\n        id\n        lineType\n        odds\n        playerProp {\n          ...PlayerPropLineFragment\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropLineFragment on PlayerPropLine {\n  id\n  line\n  over\n  under\n  suspended\n  balanced\n  name\n  player {\n    id\n    name\n    __typename\n  }\n  market {\n    id\n    stat {\n      name\n      value\n      __typename\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        data {\n          ... on SportFixtureDataMatch {\n            competitors {\n              ...CompetitorFragment\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CompetitorFragment on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  __typename\n}\n"
            # Below is a CUSTOMIZED query.
            "query": "query highrollerSportBets($limit: Int!) {\n  highrollerSportBets(limit: $limit) {\n    ...SportRootBet\n    __typename\n  }\n}\n\nfragment SportRootBet on Bet {\n  id\n  iid\n  bet {\n    ... on SportBet {\n      active\n      amount\n      cashoutMultiplier\n      createdAt\n      currency\n      id\n      payout\n      payoutMultiplier\n      potentialMultiplier\n      updatedAt\n      status\n      user {\n        id\n        name\n        __typename\n      }\n      outcomes {\n        odds\n        fixture {\n          name\n          data {\n            ... on SportFixtureDataMatch {\n              startTime\n              competitors {\n                name\n                abbreviation\n                __typename\n              }\n              __typename\n            }\n            ... on SportFixtureDataOutright {\n              name\n              startTime\n              endTime\n              __typename\n            }\n            __typename\n          }\n          tournament {\n            name\n            category {\n              name\n              sport {\n                slug\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ... on PlayerPropBet {\n      active\n      amount\n      cashoutMultiplier\n      createdAt\n      currency\n      id\n      odds\n      payout\n      payoutMultiplier\n      updatedAt\n      status\n      user {\n        id\n        name\n        __typename\n      }\n      playerProps {\n        id\n        lineType\n        odds\n        playerProp {\n          ...PlayerPropLineFragment\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropLineFragment on PlayerPropLine {\n  id\n  line\n  over\n  under\n  suspended\n  balanced\n  name\n  player {\n    id\n    name\n    __typename\n  }\n  market {\n    id\n    stat {\n      name\n      value\n      __typename\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        data {\n          ... on SportFixtureDataMatch {\n            competitors {\n              ...CompetitorFragment\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CompetitorFragment on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  __typename\n}\n"
        }
        result = self.send_graphql_request(request_data)
        if 'errors' in result:
            raise ValueError(f"Failed to request highroller sport bets: {result}")
        return result['data']['highrollerSportBets']   # returns a list

    def get_all_sport_bets(self, limit=40):
        # LIMIT can't be above 50.
        request_data = {
            "operationName": "AllSportBets",
            "variables": {"limit": limit},
            # Below is the official query.
            # "query":"query AllSportBets($limit: Int!) {\n  allSportBets(limit: $limit) {\n    ...SportRootBet\n    __typename\n  }\n}\n\nfragment SportRootBet on Bet {\n  id\n  iid\n  bet {\n    ... on SportBet {\n      active\n      amount\n      cashoutMultiplier\n      createdAt\n      currency\n      id\n      payout\n      payoutMultiplier\n      potentialMultiplier\n      updatedAt\n      status\n      user {\n        id\n        name\n        __typename\n      }\n      outcomes {\n        odds\n        fixture {\n          name\n          data {\n            ... on SportFixtureDataMatch {\n              startTime\n              competitors {\n                name\n                abbreviation\n                __typename\n              }\n              __typename\n            }\n            ... on SportFixtureDataOutright {\n              name\n              startTime\n              endTime\n              __typename\n            }\n            __typename\n          }\n          tournament {\n            category {\n              sport {\n                slug\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ... on PlayerPropBet {\n      active\n      amount\n      cashoutMultiplier\n      createdAt\n      currency\n      id\n      odds\n      payout\n      payoutMultiplier\n      updatedAt\n      status\n      user {\n        id\n        name\n        __typename\n      }\n      playerProps {\n        id\n        lineType\n        odds\n        playerProp {\n          ...PlayerPropLineFragment\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropLineFragment on PlayerPropLine {\n  id\n  line\n  over\n  under\n  suspended\n  balanced\n  name\n  player {\n    id\n    name\n    __typename\n  }\n  market {\n    id\n    stat {\n      name\n      value\n      __typename\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        data {\n          ... on SportFixtureDataMatch {\n            competitors {\n              ...CompetitorFragment\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CompetitorFragment on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  __typename\n}\n"
            # Below is a CUSTOMIZED query.
            "query":"query AllSportBets($limit: Int!) {\n  allSportBets(limit: $limit) {\n    ...SportRootBet\n    __typename\n  }\n}\n\nfragment SportRootBet on Bet {\n  id\n  iid\n  bet {\n    ... on SportBet {\n      active\n      amount\n      cashoutMultiplier\n      createdAt\n      currency\n      id\n      payout\n      payoutMultiplier\n      potentialMultiplier\n      updatedAt\n      status\n      user {\n        id\n        name\n        __typename\n      }\n      outcomes {\n        odds\n        fixture {\n          name\n          data {\n            ... on SportFixtureDataMatch {\n              startTime\n              competitors {\n                name\n                abbreviation\n                __typename\n              }\n              __typename\n            }\n            ... on SportFixtureDataOutright {\n              name\n              startTime\n              endTime\n              __typename\n            }\n            __typename\n          }\n          tournament {\n            name\n            category {\n              name\n              sport {\n                slug\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    ... on PlayerPropBet {\n      active\n      amount\n      cashoutMultiplier\n      createdAt\n      currency\n      id\n      odds\n      payout\n      payoutMultiplier\n      updatedAt\n      status\n      user {\n        id\n        name\n        __typename\n      }\n      playerProps {\n        id\n        lineType\n        odds\n        playerProp {\n          ...PlayerPropLineFragment\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropLineFragment on PlayerPropLine {\n  id\n  line\n  over\n  under\n  suspended\n  balanced\n  name\n  player {\n    id\n    name\n    __typename\n  }\n  market {\n    id\n    stat {\n      name\n      value\n      __typename\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        data {\n          ... on SportFixtureDataMatch {\n            competitors {\n              ...CompetitorFragment\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CompetitorFragment on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  __typename\n}\n"
        }
        result = self.send_graphql_request(request_data)
        if 'errors' in result:
            raise ValueError(f"Failed to request all sport bets: {result}")
        return result['data']['allSportBets']   # returns a list

    def get_bet_lookup(self, iid):
        # parameter iid example: "sport:15684378"
        # Browser visit: https://stake.com/?modal=bet&iid={iid}
        request_data = {
            "operationName": "BetLookup",
            "variables": {"iid": iid},
            "query": "query BetLookup($iid: String, $betId: String) {\n  bet(iid: $iid, betId: $betId) {\n    ...BetFragment\n    __typename\n  }\n}\n\nfragment BetFragment on Bet {\n  id\n  iid\n  type\n  scope\n  game {\n    name\n    icon\n    __typename\n  }\n  bet {\n    ... on CasinoBet {\n      ...CasinoBetFragment\n      __typename\n    }\n    ... on MultiplayerCrashBet {\n      ...MultiplayerCrashBet\n      __typename\n    }\n    ... on MultiplayerSlideBet {\n      ...MultiplayerSlideBet\n      __typename\n    }\n    ... on SoftswissBet {\n      ...SoftswissBet\n      __typename\n    }\n    ... on SportBet {\n      ...SportBet\n      __typename\n    }\n    ... on EvolutionBet {\n      ...EvolutionBet\n      __typename\n    }\n    ... on PlayerPropBet {\n      ...PlayerPropBetFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CasinoBetFragment on CasinoBet {\n  id\n  active\n  payoutMultiplier\n  amountMultiplier\n  amount\n  payout\n  updatedAt\n  currency\n  game\n  user {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment MultiplayerCrashBet on MultiplayerCrashBet {\n  id\n  user {\n    id\n    name\n    __typename\n  }\n  payoutMultiplier\n  gameId\n  amount\n  payout\n  currency\n  result\n  updatedAt\n  cashoutAt\n  btcAmount: amount(currency: btc)\n  __typename\n}\n\nfragment MultiplayerSlideBet on MultiplayerSlideBet {\n  id\n  user {\n    id\n    name\n    __typename\n  }\n  payoutMultiplier\n  gameId\n  amount\n  payout\n  currency\n  slideResult: result\n  updatedAt\n  cashoutAt\n  btcAmount: amount(currency: btc)\n  active\n  createdAt\n  __typename\n}\n\nfragment SoftswissBet on SoftswissBet {\n  id\n  amount\n  currency\n  updatedAt\n  payout\n  payoutMultiplier\n  user {\n    id\n    name\n    __typename\n  }\n  softswissGame: game {\n    id\n    name\n    edge\n    extId\n    provider {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SportBet on SportBet {\n  id\n  amount\n  active\n  currency\n  status\n  payoutMultiplier\n  potentialMultiplier\n  cashoutMultiplier\n  payout\n  createdAt\n  user {\n    id\n    name\n    __typename\n  }\n  outcomes {\n    odds\n    status\n    outcome {\n      id\n      name\n      active\n      odds\n      __typename\n    }\n    market {\n      ...MarketFragment\n      fixture {\n        id\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    fixture {\n      ...FixturePreviewFragment\n      __typename\n    }\n    __typename\n  }\n  adjustments {\n    id\n    payoutMultiplier\n    updatedAt\n    createdAt\n    __typename\n  }\n  __typename\n}\n\nfragment MarketFragment on SportMarket {\n  id\n  name\n  status\n  extId\n  specifiers\n  outcomes {\n    id\n    active\n    name\n    odds\n    __typename\n  }\n  __typename\n}\n\nfragment FixturePreviewFragment on SportFixture {\n  id\n  extId\n  status\n  slug\n  marketCount(status: [active, suspended])\n  data {\n    ...FixtureDataMatchFragment\n    ...FixtureDataOutrightFragment\n    __typename\n  }\n  eventStatus {\n    ...FixtureEventStatus\n    __typename\n  }\n  tournament {\n    ...TournamentTreeFragment\n    __typename\n  }\n  ...LiveStreamExistsFragment\n  __typename\n}\n\nfragment FixtureDataMatchFragment on SportFixtureDataMatch {\n  startTime\n  competitors {\n    ...CompetitorFragment\n    __typename\n  }\n  __typename\n}\n\nfragment CompetitorFragment on SportFixtureCompetitor {\n  name\n  extId\n  countryCode\n  abbreviation\n  __typename\n}\n\nfragment FixtureDataOutrightFragment on SportFixtureDataOutright {\n  name\n  startTime\n  endTime\n  __typename\n}\n\nfragment FixtureEventStatus on SportFixtureEventStatus {\n  homeScore\n  awayScore\n  matchStatus\n  clock {\n    matchTime\n    remainingTime\n    __typename\n  }\n  periodScores {\n    homeScore\n    awayScore\n    matchStatus\n    __typename\n  }\n  currentServer {\n    extId\n    __typename\n  }\n  homeGameScore\n  awayGameScore\n  statistic {\n    yellowCards {\n      away\n      home\n      __typename\n    }\n    redCards {\n      away\n      home\n      __typename\n    }\n    corners {\n      home\n      away\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TournamentTreeFragment on SportTournament {\n  id\n  name\n  slug\n  category {\n    id\n    name\n    slug\n    sport {\n      id\n      name\n      slug\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment LiveStreamExistsFragment on SportFixture {\n  abiosStream {\n    exists\n    __typename\n  }\n  betradarStream {\n    exists\n    __typename\n  }\n  diceStream {\n    exists\n    __typename\n  }\n  __typename\n}\n\nfragment EvolutionBet on EvolutionBet {\n  id\n  amount\n  currency\n  createdAt\n  payout\n  payoutMultiplier\n  user {\n    id\n    name\n    __typename\n  }\n  softswissGame: game {\n    id\n    name\n    edge\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropBetFragment on PlayerPropBet {\n  active\n  amount\n  cashoutMultiplier\n  createdAt\n  currency\n  id\n  odds\n  payout\n  payoutMultiplier\n  updatedAt\n  status\n  user {\n    id\n    name\n    __typename\n  }\n  playerProps {\n    id\n    lineType\n    odds\n    playerProp {\n      ...PlayerPropLineFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PlayerPropLineFragment on PlayerPropLine {\n  id\n  line\n  over\n  under\n  suspended\n  balanced\n  name\n  player {\n    id\n    name\n    __typename\n  }\n  market {\n    id\n    stat {\n      name\n      value\n      __typename\n    }\n    game {\n      id\n      fixture {\n        id\n        name\n        data {\n          ... on SportFixtureDataMatch {\n            competitors {\n              ...CompetitorFragment\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        tournament {\n          id\n          category {\n            id\n            sport {\n              id\n              name\n              slug\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"
        }
        return self.send_graphql_request(request_data)

    def get_user_balances(self):
        """
        If the access token is wrong, the response would be
          {'errors': [{'path': ['user'], 'message': 'You are not allowed to do that.', 'errorType': 'permission'}], 
           'data': {'user': None}}
        """
        request_data = {
            "operationName": "UserVaultBalances",
            "variables": {},
            "query":"query UserVaultBalances {\n  user {\n    id\n    balances {\n      available {\n        amount\n        currency\n        __typename\n      }\n      vault {\n        amount\n        currency\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
        return self.send_graphql_request(request_data)



# if __name__ == '__main__':
#     c = StakePythonClient()
#     print(c.get_bet_lookup("sport:15694993"))


