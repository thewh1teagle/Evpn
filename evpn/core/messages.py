# pylint: disable=too-few-public-methods
class MessagesV1:
    """
    Native messaging messages
    For current version on Windows
    """
    get_locations = "GetLocations"
    get_status = "GetStatus"
    connect = "Connect"
    disconnect = "Disconnect"


class MessagesV2:
    """
    Native messaging messages
    For Linux, MacOS and old version on Windows
    """
    get_locations = "XVPN.GetLocations"
    get_status = "XVPN.GetStatus"
    connect = "XVPN.Connect"
    disconnect = "XVPN.Disconnect"
