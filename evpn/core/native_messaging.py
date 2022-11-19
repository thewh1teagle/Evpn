import struct
import sys
import json


class NativeMessaging:
    """
    Class for sending native messages using native messaging protocol
    https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging
    """
    @staticmethod
    def get_message(fd):
        raw_length = fd.read(4)
        if len(raw_length) == 0:
            sys.exit(0)
        message_length = struct.unpack("@I", raw_length)[0]
        message = fd.read(message_length).decode("utf-8")
        return json.loads(message)

    # Encode a message for transmission, given its content.

    @staticmethod
    def encode_message(message_content):
        encoded_content = json.dumps(message_content).encode("utf-8")
        encoded_length = struct.pack("@I", len(encoded_content))
        return {"length": encoded_length, "content": encoded_content}

    # Send an encoded message to stdout.

    @staticmethod
    def send_message(fd, encoded_message):
        fd.write(encoded_message["length"])
        fd.write(encoded_message["content"])
        fd.flush()
