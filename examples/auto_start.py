import evpn
import time

with evpn.ExpressVpnApi(debug_prints=True) as api:
    if not api.express_vpn_running():
        print("starting...")
        api.start_express_vpn()
        time.sleep(5) # Wait for App to start
    api.connect(name="Israel")