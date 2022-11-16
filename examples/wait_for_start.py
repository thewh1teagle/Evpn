from evpn import ExpressVpnApi
import time

with ExpressVpnApi() as api:
    country_name = "Israel"
    if not api.express_vpn_running():
        api.start_express_vpn()
        time.sleep(5)
    print(f"Connecting to {country_name}")
    api.connect(name=country_name)
    time.sleep(0.5)
    while not api.is_connected():
        print("Waiting for connection...")
        time.sleep(0.5)
    print("Connected")