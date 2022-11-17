from .MessageApi import MessageApi
from .Messages import Messages
from subprocess import Popen, PIPE, call
import pathlib
import time
import platform
import psutil
import json

class ExpressVpnApi:

    EXTENSION_ID = "fgddmllnllkalaagkghckoinaemmogpe"
    MESSAGE_API = MessageApi()
    DEBUG: bool
    SERVICE_PATH = {
        "Windows": "C:\\Program Files (x86)\\ExpressVPN\\services\\ExpressVPN.BrowserHelper.exe",
        "Linux": "/usr/bin/expressvpn-browser-helper",
        "Darwin": "/usr/bin/expressvpn-browser-helper"
    }
    PROGRAM_PATH = {
        "Windows": "C:\\Program Files (x86)\\ExpressVPN\\expressvpn-ui\\ExpressVPN.exe",
        "Linux": "/usr/bin/expressvpn",
        "Darwin": "/usr/bin/expressvpn"
    }

    program_proc_name = {
        "Windows": "ExpressVPN.exe",
        "Linux": "ExpressVPN",
        "Darwin": "ExpressVPN"
    }

    messages = Messages()

    def __init__(self, debug = False) -> None:
        
        self.DEBUG = debug
        self._start_service()
        connected = False
        self._debug_print("Connecting To Daemon")
        while not connected:
            message = self._get_message()
            connected = message.get("connected")
            time.sleep(0.3)
        self._debug_print("Connected To Daemon")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _debug_print(self, data):
        if self.DEBUG:
            print(data)

    @property
    def _program_proc_name(self):
        platform_name = platform.system()
        return self.program_proc_name.get(platform_name)
    
    @property
    def _program_path(self):
        platform_name = platform.system()
        path = self.PROGRAM_PATH.get(platform_name)
        if not path:
            raise FileNotFoundError("Can't find ExpressVPN browserhelper service path")
        return pathlib.Path(path)
    
    @property
    def _service_path(self):
        platform_name = platform.system()
        path = self.SERVICE_PATH.get(platform_name)
        if not path:
            raise FileNotFoundError("Can't find ExpressVPN browserhelper service path")
        return pathlib.Path(path)

    def _build_request(self, method, params = {}):
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

    def _get_event(self):
        while True:
            message = self.MESSAGE_API.get_message(self.p.stdout)
            
            self._debug_print(f"Got event: {json.dumps(message)}")
            msg_type = message.get("type")
            if msg_type and msg_type == "event":
                return message
    
    def _get_response(self):
        while True:
            message = self.MESSAGE_API.get_message(self.p.stdout)
            self._debug_print(f"Got message: {json.dumps(message)}")
            msg_type = message.get("type")
            if msg_type and msg_type == "method":
                return message

    def _get_message(self):
        while True:
            message = self.MESSAGE_API.get_message(self.p.stdout)
            self._debug_print(f"Got message: {json.dumps(message)}")
            msg_type = message.get("type")
            if not msg_type or msg_type not in ("event"):
                return message
    
    def _send_message(self, message):
        self._debug_print("Sending: " + json.dumps(message))
        self.p.stdout.flush() # Flush output first
        self.MESSAGE_API.send_message(self.p.stdin, self.MESSAGE_API.encode_message(message))
    
    def _start_service(self): 
        path = self._service_path.absolute()
        self.p = Popen([path, f"chrome-extension://{self.EXTENSION_ID}/"], stdout=PIPE, stdin=PIPE, stderr=PIPE)

    @property
    def locations(self):
        if getattr(self, "_locations", None) is None:
            locations = self.get_locations()
            if platform.system() == "Windows":
                self._locations = [{"id": i["id"], "name": i["name"], "country_code": i["country_code"]} for i in locations["data"]["locations"]]
            else:
                self._locations = [{"id": i["id"], "name": i["country"], "country_code": i["country_code"] } for i in locations["locations"]]
        return self._locations

    def start_express_vpn(self):
        if platform.system() != "Windows":
            raise NotImplementedError("You can use start_express_vpn method only in Windows.")
        path = self._program_path
        Popen([path], start_new_session=True)

    def get_locations(self):
        req = self._build_request(self.messages.get_locations)
        self._send_message(req)
        if platform.system() == "Windows":
            return self._get_response()
        else:
            return self._get_message()

    def express_vpn_running(self) -> bool:
        if platform.system() == "Windows":
            proc_names = [p.name() for p in psutil.process_iter()]
            return self._program_proc_name in proc_names
        else:
            stat = call(["systemctl", "is-active", "--quiet", "expressvpn.service"])
            return stat == 0

    def get_status(self):
        self._debug_print("Getting status...")
        req = self._build_request(self.messages.get_status)
        self._send_message(req)
        if platform.system() == "Windows":
            return self._get_response()
        else:
            while True:
                res = self._get_message()
                if res.get("info"):
                    return res
                time.sleep(0.1)

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
        if platform.system() == "Windows":
            data = status.get("data")
            if isinstance(data, dict):
                info = data.get("info", {})
                return isinstance(info, dict) and info.get("state") == "connected"
            else:
                return False
        else:
            return bool(status.get("info").get("connected"))
        

    def disconnect(self):
        req = self._build_request(self.messages.disconnect)
        self._send_message(req)
        return self._get_message()
    
    def close(self):
        time.sleep(1.5)
        self.p.kill()
