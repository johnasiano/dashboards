import json
import requests

parameters = {
    "order": 'order',
    "per-page": 130,
    "minimum-liquidity": 5000,
    "markets-limit":100,
}

response = requests.get(url="https://api.matchbook.com/edge/rest/events", params=parameters)

data_dict = response.json()

for x in range(len(data_dict['events'])):
    try:
        event = data_dict['events'][x]
        sport = event["meta-tags"][0]["name"]
        date_time = event["start"]
        for x in event["markets"]:
            for y in x["runners"]:
                for z in y["prices"]:
                    amount_spent = z["available-amount"]
                    amount_spent = int(amount_spent)
                    print(str(amount_spent) + ' spent on ' + sport + ' on ' + date_time)
    except:
        print('pass')
