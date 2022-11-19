from evpn import ExpressVpnApi
import random

with ExpressVpnApi() as api:
    locations = api.locations
    loc = random.choice(locations)
    api.connect(loc["id"])
