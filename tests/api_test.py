import sys
import pathlib
import time
from evpn import ExpressVpnApi


LIB_PATH = str(pathlib.Path(__file__).parent.absolute() / "..")
sys.path.insert(0, LIB_PATH)
# pylint: disable=wrong-import-position
api = ExpressVpnApi(debug=True)


def test_start_vpn():
    api.start_express_vpn()


def test_connect():
    api.connect("160")
    api.wait_for_connection(timeout=60)
    assert api.is_connected() is True


def test_is_running():
    res = api.express_vpn_running()
    print(res)


def test_locations():
    locations = api.locations
    print(locations)


def test_disconnect():
    api.disconnect()
    time.sleep(1)
    assert not api.is_connected()


def test_get_status():
    res = api.get_status()
    print(res)


def pytest_sessionfinish(_session, _exitstatus):
    """ whole test run finishes. """
    api.close()
