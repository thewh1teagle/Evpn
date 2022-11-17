from evpn import ExpressVpnApi
import time
import random

with ExpressVpnApi(debug=True) as api:
    locations = api.locations # get list of all locations with ids
    location = random.choice(locations) # get random location
    api.connect(country_id=location["id"])