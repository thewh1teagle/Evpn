import sys
import pathlib
import time

lib_path = str(pathlib.Path(__file__).parent.absolute() / "..")
sys.path.insert(0, lib_path)
from evpn import ExpressVpnApi

api = ExpressVpnApi(debug_prints=False)

def test_start_vpn():
    api.start_express_vpn()


def test_umanize_locations():
    res = api.get_humanize_locations()
    assert isinstance(res, list)

def test_locations():
    res = api.get_locations()
    assert isinstance(res, dict)


def test_connect():
    api.connect(country_id="120")
    time.sleep(5)
    assert api.is_connected() == True
    
def test_disconnect():
    api.disconnect()
    time.sleep(2)
    assert not api.is_connected()