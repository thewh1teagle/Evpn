from .MessageApi import MessageApi
from .Messages import Messages
from subprocess import Popen, PIPE
import pathlib
import time
import platform
import psutil
import json
import io

class ExpressVpnApi:
    extension_id = "fgddmllnllkalaagkghckoinaemmogpe"
    message_api = MessageApi()
    debug_prints: bool
    service_path = {
        "Windows": "C:\Program Files (x86)\ExpressVPN\services\ExpressVPN.BrowserHelper.exe",
        "Linux": "/usr/bin/expressvpn-browser-helper",
        "Darwin": "/usr/bin/expressvpn-browser-helper"
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

    messages = Messages()

    def __init__(self, debug_prints = False) -> None:
        
        self.debug_prints = debug_prints
        self._start_service()
        connected = False
        if self.debug_prints:
            print("Connecting To Daemon")
        while not connected:
            message = self._get_message()
            connected = message.get("connected")
            time.sleep(0.3)
        if self.debug_prints:
            print("Connected To Daemon")

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
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

    def _get_event(self):
        while True:
            message = self.message_api.get_message(self.p.stdout)
            if (self.debug_prints):
                print(f"Got event: {json.dumps(message)}")
            msg_type = message.get("type")
            if msg_type and msg_type == "event":
                return message
    
    def _get_response(self):
        while True:
            message = self.message_api.get_message(self.p.stdout)
            if (self.debug_prints):
                print(f"Got message: {json.dumps(message)}")
            msg_type = message.get("type")
            if msg_type and msg_type == "method":
                return message

    def _get_message(self):
        while True:
            message = self.message_api.get_message(self.p.stdout)
            if (self.debug_prints):
                print(f"Got message: {json.dumps(message)}")
            msg_type = message.get("type")
            if not msg_type or msg_type not in ("event"):
                return message
    
    def _send_message(self, message):
        if self.debug_prints:
            print("Sending: " + json.dumps(message))
        self.p.stdout.flush() # Flush output first
        self.message_api.send_message(self.p.stdin, self.message_api.encode_message(message))

    def start_express_vpn(self):
        if platform.system() != "Windows":
            raise NotImplementedError("You can use start_express_vpn method only in Windows.")
        path = self._program_path()
        Popen([path], start_new_session=True)

    def _start_service(self): 
        path = self._service_path().absolute()
        self.p = Popen([path, f"chrome-extension://{self.extension_id}/"], stdout=PIPE, stdin=PIPE, stderr=PIPE)

    def get_locations(self):
        req = self._build_request(self.messages.get_locations)
        self._send_message(req)
        return self._get_response()
    
    def get_status(self):
        print("Getting status...")
        req = self._build_request(self.messages.get_status)
        self._send_message(req)
        res = self._get_response()
        print("Done")
        return res

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
        req = self._build_request(self.messages.connect, params)
        self._send_message(req)

    def is_connected(self):
        status = self.get_status()
        data = status.get("data")
        if isinstance(data, dict):
            info = data.get("info", {})
            return isinstance(info, dict) and info.get("state") == "connected"
        else:
            return False
        

    def disconnect(self):
        req = self._build_request(self.messages.disconnect)
        self._send_message(req)
        return self._get_message()
    
    def close(self):
        time.sleep(1.5)
        self.p.kill()
