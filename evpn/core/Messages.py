from abc import abstractproperty

class AbcMessages:
    @abstractproperty
    def get_locations(self):
        raise NotImplementedError

    @abstractproperty
    def get_status(self):
        raise NotImplementedError

    @abstractproperty
    def connect(self):
        raise NotImplementedError
    
    @abstractproperty
    def disconnect(self):
        raise NotImplementedError

class LinuxMessages(AbcMessages):
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

class WindowsMessages(AbcMessages):
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
