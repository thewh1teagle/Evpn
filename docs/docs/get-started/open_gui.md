---
sidebar_position: 4
---

# Open GUI interface

Open the GUI of express vpn \[Windows\]

Use pip and exuecute the following
Create a file `open_gui.py`:

```py title="open_gui.py"
from evpn import ExpressVpnApi

with ExpressVpnApi() as api:
    api.start_express_vpn() # will open the gui program in Windows
test
```