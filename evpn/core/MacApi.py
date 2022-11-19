from .AbcApi import AbcApi
from .Messages import LinuxMessages
import pathlib
from subprocess import call
import time
import json

class MacApi(AbcApi):
    
    @property
    def _program_proc_name(self):
        return "ExpressVPN"
    
    @property
    def _program_path(self):
        return "/Applications/ExpressVPN.app/Contents/ExpressVPN"

    @property
    def _service_path(self):
        return pathlib.Path("/Applications/ExpressVPN.app/Contents/expressvpn-browser-helper")
    
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
        return self._get_response()
    
    def express_vpn_running(self):
        raise NotImplementedError
    
    def _get_response(self):
        while True:
            message = self.MESSAGE_API.get_message(self.p.stdout)
            self._debug_print(f"Got message: {json.dumps(message)}")
            if message.get("type") in ("method","result") or not message.get("name"):
                return message

    def get_status(self):
        self._debug_print("Getting status...")
        req = self._build_request(self.messages.get_status)
        self._send_message(req)
        return self._get_response()

    def is_connected(self):
        status = self.get_status()
        return bool(status.get("info").get("connected"))
    
    def connect(self, id):
        req = self._build_request(self.messages.connect, {"id": id, "change_connected_location": self.is_connected() })
        self._send_message(req)
        return self._get_response()