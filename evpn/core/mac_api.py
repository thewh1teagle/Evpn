from pathlib import Path
from functools import lru_cache
from .base_api import BaseApi


class MacApi(BaseApi):
    """Class for controlling ExpressVPN daemon on MacOS"""

    @property
    def _program_proc_name(self):
        return "ExpressVPN"

    @property
    def _program_path(self):
        return "/Applications/ExpressVPN.app/Contents/MacOS/ExpressVPN"

    @property
    def _service_path(self):
        return Path("/Applications/ExpressVPN.app/Contents/MacOS/expressvpn-browser-helper")

    @property
    @lru_cache()
    def locations(self):
        locations = self._get_locations()
        locations = locations["locations"]
        return [
            {
                "id": i["id"], "name": i["country"],
                "country_code": i["country_code"]
            } for i in locations
        ]
