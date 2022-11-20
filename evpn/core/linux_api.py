from pathlib import Path
from functools import lru_cache
from subprocess import call
from .base_api import BaseApi


class LinuxApi(BaseApi):
    """Class for controlling ExpressVPN daemon on Linux"""

    @property
    def _program_proc_name(self):
        return "ExpressVPN"

    @property
    def _program_path(self):
        return "/usr/bin/expressvpn"

    @property
    def _service_path(self):
        return Path("/usr/bin/expressvpn-browser-helper")

    @property
    @lru_cache
    def locations(self):
        locations = self._get_locations()
        return [
            {
                "id": i["id"],
                "name": i["country"],
                "country_code": i["country_code"]
            } for i in locations["locations"]
        ]

    def start_express_vpn(self):
        stat = call(["systemctl", "start", "--quiet", "expressvpn.service"])
        return stat == 0

    @property
    def express_vpn_running(self):
        stat = call(["systemctl", "is-active",
                    "--quiet", "expressvpn.service"])
        return stat == 0
