from .NativeMessaging import NativeMessaging
from subprocess import Popen, PIPE
import time
import json
from abc import abstractmethod, abstractproperty

class AbcApi:

    EXTENSION_ID = "fgddmllnllkalaagkghckoinaemmogpe"
    MESSAGE_API = NativeMessaging()
    DEBUG: bool

    def __init__(self, debug = False) -> None:
        self.DEBUG = debug
        self._start_service()
        connected = False
        self._debug_print("Connecting To Daemon")
        while not connected:
            message = self._get_message()
            connected = message.get("connected")
            time.sleep(0.3)
        self._debug_print("Connected To Daemon")

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()

    @abstractproperty
    def messages(self):
        raise NotImplementedError

    @abstractproperty
    def _program_proc_name(self):
        raise NotImplementedError
    
    @abstractproperty
    def _program_path(self):
        raise NotImplementedError

    @abstractproperty
    def _service_path(self):
        raise NotImplementedError
    
    @abstractproperty
    def locations(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_locations(self):
        raise NotImplementedError

    @abstractmethod
    def start_express_vpn():
        raise NotImplementedError
    
    @abstractmethod
    def get_locations(self):
        raise NotImplementedError
    
    @abstractmethod
    def express_vpn_running(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_status(self):
        raise NotImplementedError

    @abstractmethod
    def is_connected(self):
        raise NotImplementedError

    def _debug_print(self, data):
        if self.DEBUG:
            print(data)
    
    def _build_request(self, method, params = {}):
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

    def _get_event(self):
        while True:
            message = self.MESSAGE_API.get_message(self.p.stdout)
            
            self._debug_print(f"Got event: {json.dumps(message)}")
            msg_type = message.get("type")
            if msg_type and msg_type == "event":
                return message


    def _get_response(self):
        while True:
            message = self.MESSAGE_API.get_message(self.p.stdout)
            self._debug_print(f"Got message: {json.dumps(message)}")
            msg_type = message.get("type")
            if msg_type and msg_type == "method":
                return message

    def _get_message(self):
        while True:
            message = self.MESSAGE_API.get_message(self.p.stdout)
            self._debug_print(f"Got message: {json.dumps(message)}")
            msg_type = message.get("type")
            if not msg_type or msg_type not in ("event"):
                return message

    def _send_message(self, message):
        self._debug_print("Sending: " + json.dumps(message))
        self.p.stdout.flush() # Flush output first
        self.MESSAGE_API.send_message(self.p.stdin, self.MESSAGE_API.encode_message(message))
    
    def _start_service(self): 
        path = self._service_path.absolute()
        self.p = Popen([path, f"chrome-extension://{self.EXTENSION_ID}/"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    
    
    def get_location_id(self, name):
        found = next((l for l in self.locations if l["name"].lower() == name.lower()), None)
        if not found:
            similar = next((l for l in self.locations if name.lower() in l["name"].lower()), None)
            raise ValueError(f"Country {name} not found." + f' Did you mean {similar.get("name")}?' if similar else "")
        if (found):
            return found["id"]
    
    def wait_for_connection(self, timeout = 30):
        """
        Wait for connection after calling connect
        Raising TimeoutError if timeout reached
        Default timeout is 30 seconds
        """
        start = time.time()
        while time.time() - start <= timeout:
            if self.is_connected():
                return
            time.sleep(0.3)
        raise TimeoutError
    
    def wait_for_disconnect(self, timeout = 30):
        """
        Wait for connection after calling connect
        Raising TimeoutError if timeout reached
        Default timeout is 30 seconds
        """
        start = time.time()
        while time.time() - start <= timeout:
            if not self.is_connected():
                return
            time.sleep(0.3)
        raise TimeoutError

    
    def connect(self, id):
        raise NotImplementedError
    
    def disconnect(self):
        req = self._build_request(self.messages.disconnect)
        self._send_message(req)
        return self._get_message()
    
    def reset_state(self):
        req = self._build_request("XVPN.Reset")
        self._send_message(req)
        

    def close(self):
        time.sleep(1.5)
        self.p.kill()