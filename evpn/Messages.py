import platform

class Messages:

    @property
    def get_locations(self):
        return {
            "Windows": "GetLocations",
            "Linux": "XVPN.GetLocations",
            "Darwin": "XVPN.GetLocations"
        }.get(platform.system())

    @property
    def get_status(self):
        return {
            "Windows": "GetStatus",
            "Linux": "XVPN.GetStatus",
            "Darwin": "XVPN.GetStatus"
        }.get(platform.system())
    
    @property
    def connect(self):
        return {
            "Windows": "Connect",
            "Linux": "XVPN.Connect",
            "Darwin": "XVPN.Connect"
        }.get(platform.system())

    @property
    def disconnect(self):
        return {
            "Windows": "Disconnect",
            "Linux": "XVPN.Disconnect",
            "Darwin": "XVPN.Disconnect"
        }.get(platform.system())
