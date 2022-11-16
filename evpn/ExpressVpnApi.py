from .MessageApi import MessageApi
from subprocess import Popen, PIPE
import pathlib
import time
import platform

class ExpressVpnApi:
    extension_id = "fgddmllnllkalaagkghckoinaemmogpe"
    message_api = MessageApi()
    debug_prints: bool
    service_path = {
        "Windows": "C:\Program Files (x86)\ExpressVPN\services\ExpressVPN.BrowserHelper.exe",
        "Linux": "/usr/bin/expressvpn-browser-help",
        "Darwin": "/usr/bin/expressvpn-browser-help"
    }

    def __init__(self, debug_prints = False) -> None: 
        self.debug_prints = debug_prints
        self._start_proc()    
        for i in range(4):
            message = self.message_api.get_message(self.p.stdout)
            if self.debug_prints:
                print(message)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _service_path(self):
        platform_name = platform.system()
        path = self.service_path.get(platform_name)
        if not path:
            raise FileNotFoundError("Can't find ExpressVPN browserhelper service path")
        return pathlib.Path(path)

    def _build_request(self, method, params = {}):
        return {
            "jsonrpc": 2.0,
            "method": method,
            "params": params
        }

    def _get_message(self):
        self.p.stdout.flush()
        return self.message_api.get_message(self.p.stdout)
    
    def _send_message(self, message):
        self.message_api.send_message(self.p.stdin, self.message_api.encode_message(message))

    def _start_proc(self): 
        self.p = Popen([self._service_path().absolute(), f"chrome-extension://{self.extension_id}/"], stdout=PIPE, stdin=PIPE, stderr=PIPE)

    def get_locations(self):
        req = self._build_request("GetLocations")
        self._send_message(req)
        return self._get_message()
    
    def get_status(self):
        req = self._build_request("GetStatus")
        self._send_message(req)
        return self._get_message()

    def get_logs(self):
        req = self._build_request("GetLogs")
        self._send_message(req)
        return self._get_message()

    def get_humanize_locations(self):
        locations = self.get_locations()
        return [{"name": i["name"], "id": i["id"]} for i in locations["data"]["locations"]]

    def connect(self, country_code = None, country_id = None):
        params = {"country_code": country_code} if country_code else {"id": country_id}
        req = self._build_request("Connect", params)
        self._send_message(req)
        return self._get_message()

    def is_connected(self):
        status = self.get_status()
        info = status.get("data", {}).get("info", {})
        return isinstance(info, dict) and info.get("state") == "connected"
        

    def disconnect(self):
        req = self._build_request("Disconnect")
        self._send_message(req)
        return self._get_message()
    
    def close(self):
        time.sleep(3)
        self.p.kill()
