# Evpn

ExpressVPN python native API

Setup
```shell
pip3 install -U git+https://github.com/thewh1teagle/Evpn
```

Basic Usage
```python
from evpn import ExpressVpnApi
with ExpressVpnApi as api:
    api.connect(country_code="US")
```


Control [express VPN](https://www.expressvpn.com/vpn-software) on your machine using [Native messaging](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging) protocol.
