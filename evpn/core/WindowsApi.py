from .AbcApi import AbcApi
from .Messages import WindowsMessages
import pathlib
import psutil
from subprocess import Popen

class WindowsApi(AbcApi):
    
    @property
    def _program_proc_name(self):
        return "ExpressVPN.exe"
    
    @property
    def _program_path(self):
        return "C:\\Program Files (x86)\\ExpressVPN\\expressvpn-ui\\ExpressVPN.exe"

    @property
    def _service_path(self):
        return pathlib.Path("C:\\Program Files (x86)\\ExpressVPN\\services\\ExpressVPN.BrowserHelper.exe")
    
    @property
    def locations(self):
        if getattr(self, "_locations", None) is None:
            locations = self.get_locations()
            self._locations = [{"id": i["id"], "name": i["name"], "country_code": i["country_code"]} for i in locations["data"]["locations"]]
        return self._locations

    @property
    def messages(self):
        if getattr(self, "_messages", None) is None:
            self._messages = WindowsMessages()
        return self._messages

    def get_locations(self):
        req = self._build_request(self.messages.get_locations)
        self._send_message(req)
        return self._get_response()

    def start_express_vpn(self):
        path = self._program_path
        Popen([path], start_new_session=True)

    
    def express_vpn_running(self):
        proc_names = [p.name() for p in psutil.process_iter()]
        return self._program_proc_name in proc_names
    
    def get_status(self):
        self._debug_print("Getting status...")
        req = self._build_request(self.messages.get_status)
        self._send_message(req)
        return self._get_response()

    def is_connected(self):
        status = self.get_status()
        data = status.get("data")
        if isinstance(data, dict):
            info = data.get("info", {})
            return isinstance(info, dict) and info.get("state") == "connected"
        else:
            return False