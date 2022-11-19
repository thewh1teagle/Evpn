from subprocess import Popen, PIPE
from abc import abstractmethod
import time
import json
from tempfile import gettempdir
from .native_messaging import NativeMessaging
from .messages import AbcMessages


class BaseApi:
    """Abstract Class For Daemon API """

    EXTENSION_ID = "fgddmllnllkalaagkghckoinaemmogpe"
    MESSAGE_API = NativeMessaging()
    debug: bool
    messages: AbcMessages

    def __init__(self, debug=False) -> None:
        self._locations = None
        self.debug = debug
        self._start_service()
        self._debug_print("Connecting To Daemon")
        self._wait_for_daemon(timeout=5)
        self._debug_print("Connected To Daemon")

    def _wait_for_daemon(self, timeout):
        connected = False
        start_t = time.time()
        while not connected and time.time() - start_t < timeout:
            message = self._get_message()
            connected = message.get("connected")
            time.sleep(0.3)
        if not connected:
            raise TimeoutError("Can't connect to ExpressVPN daemon")

    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        self.close()

    @property
    @abstractmethod
    def messages(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def _program_proc_name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def _program_path(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def _service_path(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def locations(self):
        raise NotImplementedError

    @abstractmethod
    def get_locations(self):
        raise NotImplementedError

    @abstractmethod
    def start_express_vpn(self):
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
        if self.debug:
            print(data[:100] + "...")

    def _build_request(self, method, params=None):
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 200
        }

    def _get_response(self):
        raise NotImplementedError

    def _get_message(self):
        message = self.MESSAGE_API.get_message(self.proc.stdout)
        self._debug_print(f"Got message: {json.dumps(message)}")
        return message

    def _send_message(self, message):
        self._debug_print("Sending: " + json.dumps(message))
        self.proc.stdout.flush()  # Flush output first
        self.MESSAGE_API.send_message(
            self.proc.stdin, self.MESSAGE_API.encode_message(message))

    def some_method(self):
        pass

    def _start_service(self):
        path = self._service_path.absolute()
        self.proc = Popen([
            path,
            f"chrome-extension://{self.EXTENSION_ID}/"],
            stdout=PIPE, stdin=PIPE, stderr=PIPE,
            cwd=gettempdir()
        )

    def get_location_id(self, name):
        found = next(
            (l for l in self._locations if l["name"].lower() == name.lower()), None)
        if not found:
            similar = next(
                (l for l in self._locations if name.lower() in l["name"].lower()), None)
            error_msg = f"Country {name} not found. "
            error_msg += f'Did you mean {similar.get("name")}?' if similar else ""
            raise ValueError(error_msg)
        return found["id"]

    def wait_for_connection(self, timeout=30):
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

    def wait_for_disconnect(self, timeout=30):
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

    def connect(self, country_id):
        raise NotImplementedError

    def disconnect(self):
        req = self._build_request(self.messages.disconnect)
        self._send_message(req)
        return self._get_response()

    def reset_state(self):
        req = self._build_request("XVPN.Reset")
        self._send_message(req)
        return self._get_response()

    def close(self):
        time.sleep(1.5)
        self.proc.kill()
