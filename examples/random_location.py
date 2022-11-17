from evpn import ExpressVpnApi
import random
import time

with ExpressVpnApi(debug=True) as api:
    locations = api.locations # get list of all locations with ids
    location = random.choice(locations) # get random location
    api.connect(country_id=location["id"])
    time.sleep(0.5)
    