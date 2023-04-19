# Evpn
ExpressVPN python native API

Control [express VPN](https://www.expressvpn.com/vpn-software) on your machine using [Native messaging](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging) protocol.

##### Setup
```shell
pip3 install -U evpn
```

##### Basic Usage
```python
from evpn import ExpressVpnApi
import random

with ExpressVpnApi() as api:
    locations = api.locations # get available locations
    loc = random.choice(locations)
    api.connect(loc["id"])
```

##### Examples
[random_location.py](https://github.com/thewh1teagle/evpn/blob/main/examples/random_location.py)

##### About
- This library is Cross Platform (*Windows*, *Linux*, *MacOS* are supported)
- It talking to expressVPN daemon using native message protocol.

##### Development
1. Install dependencies
`pip3 install .`
2. Install dev dependencies
`pip3 install .[dev]`
3. Lint it
`pylint --rcfile=.pylintrc --recursive=y .`
4. Test your changes
`python3 -m pytest .`
5. Make new PR 🚀

##### Contributing
Every contribution is welcome. If you want to contribute but are unsure where to start, any open issues are fair game!

