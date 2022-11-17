import sys
import pathlib
import time
import platform

lib_path = str(pathlib.Path(__file__).parent.absolute() / "..")
sys.path.insert(0, lib_path)
from evpn import ExpressVpnApi
api = ExpressVpnApi(debug=True)

def test_is_running():
    res = api.express_vpn_running()
    print(res)

def test_locations():
    locations = api.locations
    print(locations)

def test_start_vpn():
    if platform.system() == "Windows":
        api.start_express_vpn()

def test_connect():
    api.connect(country_id="120")
    time.sleep(5)
    assert api.is_connected() == True
    
def test_disconnect():
    api.disconnect()
    time.sleep(2)
    assert not api.is_connected()

def test_get_status():
    res = api.get_status()
    print(res)