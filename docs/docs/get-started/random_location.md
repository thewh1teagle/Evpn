---
sidebar_position: 1
---

# Connect Random location

connect random location

Create a file `change_location.py`:

```py title="change_location.py"
from evpn import ExpressVpnApi
import random

with ExpressVpnApi() as api:
    locations = api.locations # simple list of locations
    loc = random.choice(locations) # get some location from list
    api.connect(loc["id"]) # connect using id
```