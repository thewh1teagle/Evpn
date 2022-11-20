from subprocess import Popen, PIPE
from abc import abstractmethod
import time
import json
from tempfile import gettempdir
import psutil
from .native_messaging import NativeMessaging
from .messages import MessagesV2


class BaseApi:
    """
        Class For Daemon API
        Platform specific methods are abstract
    """

    EXTENSION_ID = "fgddmllnllkalaagkghckoinaemmogpe"
    MESSAGE_API = NativeMessaging()

    def __init__(self, debug=False) -> None:
        self._messages = MessagesV2
        self._locations = None
        self._debug = debug
        self._start_service()
        self._debug_print("Connecting To Daemon")
        self._wait_for_daemon(timeout=5)
        self._debug_print("Connected To Daemon")

    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        self.close()

    def _wait_for_daemon(self, timeout):
        connected = False
        start_t = time.time()
        while not connected and time.time() - start_t < timeout:
            message = self._get_message()
            connected = message.get("connected")
            time.sleep(0.3)
        if not connected:
            raise TimeoutError("Can't connect to ExpressVPN daemon")

    def _debug_print(self, data):
        if self._debug:
            print(data[:100] + "...")

    def _build_request(self, method, params=None):
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 200
        }

    def _get_message(self):
        message = self.MESSAGE_API.get_message(self._proc.stdout)
        self._debug_print(f"Got message: {json.dumps(message)}")
        return message

    def _send_message(self, message):
        self._debug_print("Sending: " + json.dumps(message))
        self._proc.stdout.flush()  # Flush output first
        self.MESSAGE_API.send_message(
            self._proc.stdin, self.MESSAGE_API.encode_message(message))

    def _get_response(self):
        while True:
            message = self.MESSAGE_API.get_message(self._proc.stdout)
            self._debug_print(f"Got message: {json.dumps(message)}")
            if message.get("type") in ("method", "result") or not message.get("name"):
                return message

    def _call(self, message: str, params=None):
        """ Send native message and return response """
        req = self._build_request(message, params)
        self._send_message(req)
        return self._get_response()

    def _start_service(self):
        path = self._service_path.absolute()
        # pylint: disable-next=consider-using-with
        self._proc = Popen([
            path,
            f"chrome-extension://{self.EXTENSION_ID}/"],
            stdout=PIPE, stdin=PIPE, stderr=PIPE,
            cwd=gettempdir()
        )

    def _get_locations(self):
        return self._call(self._messages.get_locations)

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

    def start_express_vpn(self):
        path = self._program_path
        # Since in some platforms this process started in attached mode, we keep it running...
        # pylint: disable=consider-using-with
        Popen([path], start_new_session=True)

    @property
    def express_vpn_running(self):
        proc_names = [p.name() for p in psutil.process_iter()]
        return any(p in proc_names for p in self._program_proc_name)

    @property
    def is_connected(self):
        status = self.get_status()
        return bool(status.get("info").get("connected"))

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
            if self.is_connected:
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
            if not self.is_connected:
                return
            time.sleep(0.3)
        raise TimeoutError

    def disconnect(self):
        return self._call(self._messages.disconnect)

    def get_status(self):
        return self._call(self._messages.get_status)

    def connect(self, country_id):
        params = {"id": country_id,
                  "change_connected_location": self.is_connected}
        return self._call(self._messages.connect, params)

    def close(self):
        time.sleep(1.5)
        self._proc.kill()

    @property
    @abstractmethod
    def locations(self):
        """
        Get list of locations
        fields: name, ID, country_code
        """
        raise NotImplementedError
