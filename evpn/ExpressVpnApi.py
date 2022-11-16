from .MessageApi import MessageApi
from subprocess import Popen, PIPE
import pathlib
import time
import platform
import psutil
import json

class ExpressVpnApi:
    extension_id = "fgddmllnllkalaagkghckoinaemmogpe"
    message_api = MessageApi()
    debug_prints: bool
    service_path = {
        "Windows": "C:\Program Files (x86)\ExpressVPN\services\ExpressVPN.BrowserHelper.exe",
        "Linux": "/usr/bin/expressvpn-browser-help",
        "Darwin": "/usr/bin/expressvpn-browser-help"
    }
    program_path = {
        "Windows": "C:\Program Files (x86)\ExpressVPN\expressvpn-ui\ExpressVPN.exe",
        "Linux": "/usr/bin/expressvpn",
        "Darwin": "/usr/bin/expressvpn"
    }

    program_proc_name = {
        "Windows": "ExpressVPN.exe",
        "Linux": "ExpressVPN",
        "Darwin": "ExpressVPN"
    }

    def __init__(self, debug_prints = False) -> None: 
        self.debug_prints = debug_prints
        self._start_service()  
        for i in range(4):
            message = self.message_api.get_message(self.p.stdout)
            if self.debug_prints:
                print(message)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def locations(cls):
        if getattr(cls, "_locations", None) is None:
            cls._locations = cls.get_humanize_locations()
        return cls._locations

    def _program_proc_name(self):
        platform_name = platform.system()
        return self.program_proc_name.get(platform_name)

    def _program_path(self):
        platform_name = platform.system()
        path = self.program_path.get(platform_name)
        if not path:
            raise FileNotFoundError("Can't find ExpressVPN browserhelper service path")
        return pathlib.Path(path)

    def _service_path(self):
        platform_name = platform.system()
        path = self.service_path.get(platform_name)
        if not path:
            raise FileNotFoundError("Can't find ExpressVPN browserhelper service path")
        return pathlib.Path(path)

    def express_vpn_running(self) -> bool:
        proc_names = [p.name() for p in psutil.process_iter()]
        return self._program_proc_name() in proc_names


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
        if self.debug_prints:
            print("Sending: " + json.dumps(message))
        self.message_api.send_message(self.p.stdin, self.message_api.encode_message(message))

    def start_express_vpn(self):
        path = self._program_path()
        Popen([path], start_new_session=True)

    def _start_service(self): 
        path = self._service_path().absolute()
        self.p = Popen([path, f"chrome-extension://{self.extension_id}/"], stdout=PIPE, stdin=PIPE, stderr=PIPE)

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

    def get_location_id(self, name):
        found = next((l for l in self.locations if l["name"].lower() == name.lower()), None)
        if not found:
            similar = next((l for l in self.locations if name.lower() in l["name"].lower()), None)
            raise ValueError(f"Country {name} not found." + f' Did you mean {similar.get("name")}?' if similar else "")
        if (found):
            return found["id"]


    def connect(self, name = None, country_code = None, country_id = None):
        if not any([name,country_code,country_id]):
            raise ValueError("You must provide either name, country_code, or country_id parameter to connect")
        params = {"country_code": country_code} if country_code else {"id": country_id or self.get_location_id(name)}
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
        time.sleep(1.5)
        self.p.kill()
