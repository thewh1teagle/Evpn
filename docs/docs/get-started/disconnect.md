---
sidebar_position: 2
---

# Disconnect

Disconnect from the vpn

Create a file `change_location.py`:

```py title="disconnect.py"
from evpn import ExpressVpnApi

with ExpressVpnApi() as api:
    api.disconnect()
```