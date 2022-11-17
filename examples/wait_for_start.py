from evpn import ExpressVpnApi
import time

def wait_for_connection(api: ExpressVpnApi):
    while not api.is_connected():
        print("Waiting for connection...")
        time.sleep(0.5)
    print("Connected")

with ExpressVpnApi() as api:
    country_name = "Israel"
    if not api.express_vpn_running():
        api.start_express_vpn()
        time.sleep(5)
    
    print(f"Connecting to {country_name}...")
    api.connect(name=country_name)
    api.wait_for_connection(5)
    print("Connected!")
