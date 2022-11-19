import platform

_name = platform.system()

if _name == "Windows":
    from .core.windows_api import WindowsApi as ExpressVpnApi
elif _name == "Linux":
    from .core.linux_api import LinuxApi as ExpressVpnApi
elif _name == "Darwin":
    from .core.mac_api import MacApi as ExpressVpnApi
else:
    raise NotImplementedError(f"Can't run on {_name} platform.")


__all__ = ['ExpressVpnApi']
