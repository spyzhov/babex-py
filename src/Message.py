from .Path import Path
try:
    import ujson as json
except ImportError:
    import json


class Message(object):
    def __init__(self, channel, body, method, properties):
        self.channel = channel
        self.method = method
        self.payload = json.loads(body.decode())
        self.data = self.payload.get('data', None)
        self.chain = [Path(item) for item in self.payload.get('chain', [])]
        self.config = self.payload.get('config', None)
        self.headers = properties.headers or {}

    def ack(self):
        self.channel.basic_ack(delivery_tag=self.method.delivery_tag)

    def get_current(self):
        for index, path in enumerate(self.chain):
            if not path.successful:
                return index, path
        return None, None
