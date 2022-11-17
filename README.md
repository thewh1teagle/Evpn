# Evpn

ExpressVPN python native API

Control [express VPN](https://www.expressvpn.com/vpn-software) on your machine using [Native messaging](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging) protocol.

##### Setup
```shell
pip3 install -U git+https://github.com/thewh1teagle/Evpn
```

##### Basic Usage
```python
from evpn import ExpressVpnApi
with ExpressVpnApi() as api:
    api.connect(country_code="US")
```

##### Examples
[random_location.py](https://github.com/thewh1teagle/Evpn/blob/main/examples/random_location.py)  
[wait_for_start.py](https://github.com/thewh1teagle/Evpn/blob/main/examples/wait_for_start.py)

##### Contributing
Every contribution is welcome. If you want to contribute but are unsure where to start, any open issues are fair game! 

