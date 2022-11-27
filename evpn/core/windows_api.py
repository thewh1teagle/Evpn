from pathlib import Path
from functools import lru_cache
from .base_api import BaseApi
from .messages import MessagesV1, MessagesV2


class WindowsApi(BaseApi):
    """Class for controlling ExpressVPN daemon on Windows"""

    def __init__(self, debug=False) -> None:
        super().__init__(debug)
        self._messages = MessagesV2() if self._is_old_version else MessagesV1()

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
    @lru_cache()
    def _service_path(self):
        paths = [
            Path(
                "C:\\Program Files (x86)\\ExpressVPN\\services\\ExpressVPN.BrowserHelper.exe"),
            Path(
                "C:\\Program Files (x86)\\ExpressVPN\\expressvpnd\\expressvpn-browser-helper.exe")
        ]
        for path in paths:
            if path.exists():
                return path
        raise Exception("Can't find browser service path of expressVPN")

    @property
    @lru_cache()
    def locations(self):
        locs = self._get_locations()
        locs = locs["locations"] if self._is_old_version else locs["data"]["locations"]
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
    def _is_old_version(self):
        # lowercase suffix = old version
        return self._service_path.name.endswith('expressvpn-browser-helper.exe')

    @property
    def is_connected(self):
        if self._is_old_version:
            return super().is_connected
        status = self.get_status()
        data = status.get("data")
        if isinstance(data, dict):
            info = data.get("info", {})
            return isinstance(info, dict) and info.get("state") == "connected"
        return False

    def connect(self, country_id):
        if self._is_old_version:
            super().connect(country_id)
        return self._call(self._messages.connect, {"id": country_id})
