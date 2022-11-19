import platform

_name = platform.system()

if _name == "Windows":
    from .core.WindowsApi import WindowsApi as ExpressVpnApi
elif _name == "Linux":
    from .core.LinuxApi import LinuxApi as ExpressVpnApi
elif _name == "Darwin":
    from .core.MacApi import MacApi as ExpressVpnApi
else:
    raise NotImplementedError(f"Can't run on {_name} platform.")


__all__ = ['ExpressVpnApi']
