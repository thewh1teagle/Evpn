import pathlib
import json
from tempfile import gettempdir
from subprocess import Popen, PIPE
import psutil
from .base_api import BaseApi
from .messages import MacMessages


class MacApi(BaseApi):
    """Class for controlling ExpressVPN daemon on MacOS"""

    _messages = MacMessages()

    @property
    def _program_proc_name(self):
        return "ExpressVPN"

    @property
    def _program_path(self):
        return "/Applications/ExpressVPN.app/Contents/MacOS/ExpressVPN"

    @property
    def _service_path(self):
        return pathlib.Path("/Applications/ExpressVPN.app/Contents/MacOS/expressvpn-browser-helper")

    def _start_service(self):
        path = self._service_path.absolute()
        self.proc = Popen([
            path,
            f"chrome-extension://{self.EXTENSION_ID}/"],
            stdout=PIPE, stdin=PIPE, stderr=PIPE,
            cwd=gettempdir()
        )

    @property
    def _locations(self):
        if getattr(self, "_locations", None) is None:
            locations = self.get_locations()
            self._locations = [{"id": i["id"], "name": i["country"],
                                "country_code": i["country_code"]} for i in locations["locations"]]
        return self._locations

    @property
    def messages(self):
        if getattr(self, "_messages", None) is None:
            self._messages = MacMessages()
        return self._messages

    def get_locations(self):
        req = self._build_request(self.messages.get_locations)
        self._send_message(req)
        return self._get_response()

    def express_vpn_running(self):
        proc_names = [p.name() for p in psutil.process_iter()]
        return any(p in proc_names for p in self._program_proc_name)

    def _get_response(self):
        while True:
            message = self.MESSAGE_API.get_message(self.proc.stdout)
            self._debug_print(f"Got message: {json.dumps(message)}")
            if message.get("type") in ("method", "result") or not message.get("name"):
                return message

    def start_express_vpn(self):
        path = self._program_path
        Popen([path], start_new_session=True)

    def get_status(self):
        self._debug_print("Getting status...")
        req = self._build_request(self.messages.get_status)
        self._send_message(req)
        return self._get_response()

    def is_connected(self):
        status = self.get_status()
        return bool(status.get("info").get("connected"))

    def connect(self, country_id):
        message = {"id": country_id,
                   "change_connected_location": self.is_connected()}
        req = self._build_request(self.messages.connect, message)
        self._send_message(req)
        return self._get_response()
