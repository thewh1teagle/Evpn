from subprocess import Popen, PIPE
import json
import pathlib
from tempfile import gettempdir
import psutil
from .base_api import BaseApi
from .messages import WindowsMessages, WindowsMessagesOld


class WindowsApi(BaseApi):
    """Class for controlling ExpressVPN daemon on Windows"""

    def __init__(self, debug=False) -> None:
        self._messages = WindowsMessagesOld() if self.is_old_version else WindowsMessages()
        super().__init__(debug)

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
            pathlib.Path(
                "C:\\Program Files (x86)\\ExpressVPN\\services\\ExpressVPN.BrowserHelper.exe"),
            pathlib.Path(
                "C:\\Program Files (x86)\\ExpressVPN\\expressvpnd\\expressvpn-browser-helper.exe")
        ]

    @property
    def locations(self):
        if getattr(self, "_locations", None) is None:
            locs = self.get_locations()
            locs = locs["locations"] if self.is_old_version else locs["data"]["locations"]
            self._locations = [
                {
                    "id": i["id"],
                    "name": i["name"],
                    "country_code": i["country_code"]
                }
                for i in locs
            ]
        return self._locations

    @property
    def is_old_version(self):
        return self._service_path[1].exists()

    @property
    def messages(self):
        return self._messages

    def _start_service(self):
        paths = self._service_path
        for path in paths:
            if path.exists():
                self.proc = Popen(
                    [path, f"chrome-extension://{self.EXTENSION_ID}/"],
                    stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=gettempdir()
                )
                return
        raise Exception("Can't find browser service path of expressVPN")

    def _get_response(self):
        while True:
            message = self.MESSAGE_API.get_message(self.proc.stdout)
            self._debug_print(f"Got message: {json.dumps(message)}")
            if message.get("type") in ("method", "result") or not message.get("name"):
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
        data = status.get("data")
        if isinstance(data, dict):
            info = data.get("info", {})
            return isinstance(info, dict) and info.get("state") == "connected"
        return False

    def connect(self, country_id):
        if self.is_old_version:
            message = {
                "id": country_id, "change_connected_location": self.is_connected()}
            req = self._build_request(self.messages.connect, message)
            self._send_message(req)
            return self._get_response()
        req = self._build_request(
            self.messages.connect, {"id": country_id})
        self._send_message(req)
        return self._get_response()
