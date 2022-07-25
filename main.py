# Import library for fetching Elspot data
from nordpool import elspot
from datetime import date, datetime
import pytz
# import pyyaml module
import yaml
from yaml.loader import SafeLoader


# Read configuration
# Open the file and load the file
with open('config.yml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    
shelly_auth_key = data["shelly_key"]
shelly_server = data["shelly_server"]
nordpol_area = data["nordpol_area"]

# Initialize class for fetching Elspot prices
prices_spot = elspot.Prices()
prices_spot.currency = "SEK"
# Fetch hourly Elspot prices for Finland and print the resulting dictionary
prices = prices_spot.hourly(areas=[nordpol_area], end_date=date.today())

current_hour = datetime.now(pytz.timezone("Europe/Stockholm")).hour
day_in_week = date.today().weekday()

for device in data["devices"]:
    print(f"Handling {device['name']}")
    on = False
    if current_hour in device["always_on_hours"]:
        on = True
    elif current_hour in device["hours"] and day_in_week in device["days"]:
        # Only run control during this time
        if prices['areas'][nordpol_area]['values'][current_hour]['value'] < device["always_on_when_price_below"] * 10:
            on = True
        else:
            day_prices = [prices['areas'][nordpol_area]['values'][hour]['value'] for hour in device["hours"]]
            day_prices.sort()            
            if prices['areas'][nordpol_area]['values'][current_hour]['value'] < day_prices[device["minimum_hours"]]:
                on = True
    if on:
        print("Turning ON")
        import requests
        url = f"https://{shelly_server}/device/relay/control/"
        data = {
            "channel": 0,
            "turn": "on",
            "id": device["shelly_id"],
            #"timer": 10,
            "auth_key": shelly_auth_key
        }
        contents = requests.post(url, data=data)

