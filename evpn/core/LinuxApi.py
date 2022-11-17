from .AbcApi import AbcApi
from .Messages import LinuxMessages
import pathlib
from subprocess import call
import time

class LinuxApi(AbcApi):
    
    @property
    def _program_proc_name(self):
        return "ExpressVPN"
    
    @property
    def _program_path(self):
        return "/usr/bin/expressvpn"

    @property
    def _service_path(self):
        return pathlib.Path("/usr/bin/expressvpn-browser-helper")
    
    @property
    def locations(self):
        if getattr(self, "_locations", None) is None:
            locations = self.get_locations()
            self._locations = [{"id": i["id"], "name": i["country"], "country_code": i["country_code"] } for i in locations["locations"]]
        return self._locations

    @property
    def messages(self):
        if getattr(self, "_messages", None) is None:
            self._messages = LinuxMessages()
        return self._messages

    def get_locations(self):
        req = self._build_request(self.messages.get_locations)
        self._send_message(req)
        return self._get_message()
    
    def express_vpn_running(self):
        stat = call(["systemctl", "is-active", "--quiet", "expressvpn.service"])
        return stat == 0
    
    def get_status(self):
        self._debug_print("Getting status...")
        req = self._build_request(self.messages.get_status)
        self._send_message(req)
        while True:
                res = self._get_message()
                if res.get("info"):
                    return res
                time.sleep(0.1)

    def is_connected(self):
        status = self.get_status()
        return bool(status.get("info").get("connected"))
    
    def connect(self, id):
        req = self._build_request(self.messages.connect, {"id": id, "change_connected_location": self.is_connected() })
        self._send_message(req)