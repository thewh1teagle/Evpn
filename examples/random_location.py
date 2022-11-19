import random
from evpn import ExpressVpnApi

with ExpressVpnApi() as api:
    locations = api.locations
    loc = random.choice(locations)
    api.connect(loc["id"])
