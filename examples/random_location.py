from evpn import ExpressVpnApi
import time
import random

with ExpressVpnApi(debug_prints=True) as api:
    locations = api.get_humanize_locations() # get list of all locations with ids
    location = random.choice(locations) # get random location
    api.connect(country_id=location["id"])
    time.sleep(5)
    api.disconnect() # disconnect vpn