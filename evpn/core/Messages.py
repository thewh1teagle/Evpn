# pylint: disable=missing-class-docstring
from abc import ABCMeta, abstractmethod


class BaseMessages(metaclass=ABCMeta):
    """
    "Abstract class for storing messages code for native messaging daemon
    """
    @property
    @abstractmethod
    def get_locations(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def get_status(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def connect(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def disconnect(self):
        raise NotImplementedError


class LinuxMessages(BaseMessages):
    @property
    def get_locations(self):
        return "XVPN.GetLocations"

    @property
    def get_status(self):
        return "XVPN.GetStatus"

    @property
    def connect(self):
        return "XVPN.Connect"

    @property
    def disconnect(self):
        return "XVPN.Disconnect"


class WindowsMessages(BaseMessages):
    @property
    def get_locations(self):
        return "GetLocations"

    @property
    def get_status(self):
        return "GetStatus"

    @property
    def connect(self):
        return "Connect"

    @property
    def disconnect(self):
        return "Disconnect"


class WindowsMessagesOld(BaseMessages):
    """
    Messages for old version of expressVPN
    """
    @property
    def get_locations(self):
        return "XVPN.GetLocations"

    @property
    def get_status(self):
        return "XVPN.GetStatus"

    @property
    def connect(self):
        return "XVPN.Connect"

    @property
    def disconnect(self):
        return "XVPN.Disconnect"


class MacMessages(BaseMessages):
    @property
    def get_locations(self):
        return "XVPN.GetLocations"

    @property
    def get_status(self):
        return "XVPN.GetStatus"

    @property
    def connect(self):
        return "XVPN.Connect"

    @property
    def disconnect(self):
        return "XVPN.Disconnect"
