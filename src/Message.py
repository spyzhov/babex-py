from .Path import Path
try:
    import ujson as json
except ImportError:
    import json


class Message(object):
    def __init__(self, channel, body, envelope, properties):
        self.channel = channel
        self.envelope = envelope
        self.payload = json.loads(body.decode())
        self.chain = [Path(item) for item in self.payload.get('chain', [])]
        self.headers = properties.get('headers', {})
        self.config = self.payload.get('config', None)

    async def ack(self):
        await self.channel.basic_client_ack(delivery_tag=self.envelope.delivery_tag)

    def get_current(self):
        for index, path in enumerate(self.chain):
            if not path.successful:
                return index, path
        return None, None
