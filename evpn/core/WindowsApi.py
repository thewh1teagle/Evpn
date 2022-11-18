import json
from .AbcApi import AbcApi
from .Messages import WindowsMessages, WindowsMessagesOld
import pathlib
import psutil
from subprocess import Popen, PIPE
from tempfile import gettempdir

class WindowsApi(AbcApi):
    
    @property
    def _program_proc_name(self):
        return [
            "ExpressVPN.exe",
            "expressvpnd.exe"
        ]
    
    @property
    def _program_path(self):
        return "C:\\Program Files (x86)\\ExpressVPN\\expressvpn-ui\\ExpressVPN.exe"

    @property
    def _service_path(self):
        return [
            pathlib.Path("C:\\Program Files (x86)\\ExpressVPN\\services\\ExpressVPN.BrowserHelper.exe"),
            pathlib.Path("C:\\Program Files (x86)\\ExpressVPN\\expressvpnd\\expressvpn-browser-helper.exe")
        ]
    
    @property
    def locations(self):
        if getattr(self, "_locations", None) is None:
            locations = self.get_locations()
            if self.is_old_version:
                self._locations = [{"id": i["id"], "name": i["name"], "country_code": i["country_code"]} for i in locations["locations"]]
            else:
                self._locations = [{"id": i["id"], "name": i["name"], "country_code": i["country_code"]} for i in locations["data"]["locations"]]
        return self._locations

    @property
    def is_old_version(self):
        return self._service_path[1].exists()

    @property
    def messages(self):
        if getattr(self, "_messages", None) is None:
            if self.is_old_version:
                self._messages = WindowsMessagesOld()
            else:
                self._messages = WindowsMessages()
        return self._messages

    def _start_service(self): 
        paths = self._service_path
        for path in paths:
            if path.exists():
                self.p = Popen([path, f"chrome-extension://{self.EXTENSION_ID}/"], stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=gettempdir())
                return
        raise Exception("Can't find browser service path of expressVPN")

    def _get_response(self):
        while True:
            message = self.MESSAGE_API.get_message(self.p.stdout)
            self._debug_print(f"Got message: {json.dumps(message)}")
            if message.get("type") in ("method","result") or not message.get("name"):
                return message

    def get_locations(self):
        req = self._build_request(self.messages.get_locations)
        self._send_message(req)
        return self._get_response()

    def start_express_vpn(self):
        path = self._program_path
        Popen([path], start_new_session=True)

    
    def express_vpn_running(self):
        proc_names = [p.name() for p in psutil.process_iter()]
        return any(p in proc_names for p in self._program_proc_name)
    
    def get_status(self):
        self._debug_print("Getting status...")
        req = self._build_request(self.messages.get_status)
        self._send_message(req)
        return self._get_response()

    def is_connected(self):
        status = self.get_status()
        if self.is_old_version:
            info = status.get("info", {})
            return isinstance(info, dict) and info.get("state") == "connected"
        else:
            data = status.get("data")
            if isinstance(data, dict):
                info = data.get("info", {})
                return isinstance(info, dict) and info.get("state") == "connected"
            else:
                return False
    def connect(self, id):
        if self.is_old_version:
            req = self._build_request(self.messages.connect, {"id": id, "change_connected_location": self.is_connected() })
            self._send_message(req)
            return self._get_response()
        else:
            req = self._build_request(self.messages.connect, {"id": id })
            self._send_message(req)
            return self._get_response()