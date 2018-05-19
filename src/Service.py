import uuid
import logging
import asyncio
import aioamqp
from .Message import Message
from .errors import ErrorDataIsNotArray, ErrorNextIsNotDefined
try:
    import ujson as json
except ImportError:
    import json


class Service:
    """
    Babex service
    """
    logger = logging.getLogger("babex")

    def __init__(self, name, address="amqp://localhost", isSingle=True, skipDeclareQueue=False, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.address = address
        self.skipDeclareQueue = skipDeclareQueue
        self.queue_name = '{}.{}'.format(name, uuid.uuid4()) if isSingle else name
        self.connection = None
        self.options = {"exclusive": True, "auto_delete": True} if isSingle else {}
        self.transport = None
        self.protocol = None
        self.channel = None
        super(Service, self).__init__()

    def __del__(self):
        if self.channel:
            self.loop.run_until_complete(self.channel.close())
        if self.protocol:
            self.loop.run_until_complete(self.protocol.close())
        if self.transport:
            self.transport.close()
        deleter = getattr(super(Service, self), "__del__", None)
        if callable(deleter):
            deleter()

    def connect(self):
        self.logger.info(f"Try to connect to {self.address}")
        self.transport, self.protocol = self.loop.run_until_complete(
            aioamqp.from_url(self.address, loop=self.loop))
        self.channel = self.loop.run_until_complete(self.protocol.channel())
        if not self.skipDeclareQueue:
            self.loop.run_until_complete(self.channel.queue_declare(queue_name=self.queue_name, **self.options))
        self.logger.info(f"waiting for messages on {self.queue_name}")
        return self

    def listen(self, callback):
        self.loop.run_until_complete(
            self.channel.basic_consume(self.__get_callback(callback), queue_name=self.queue_name))
        self.loop.run_forever()

    def bind_to_exchange(self, exchange_name, routing_key):
        self.loop.run_until_complete(
            self.channel.queue_bind(queue_name=self.queue_name, exchange_name=exchange_name, routing_key=routing_key))
        return self

    async def publish_message(self, exchange_name, routing_key, chain=None, data=None, headers=None, config=None):
        self.logger.info(f"publish message to {exchange_name}:{routing_key}")
        payload = json.dumps({
            'data': data or {},
            'chain': chain or {},
            'config': config,
        })
        await self.channel.basic_publish(
            exchange_name=str(exchange_name),
            routing_key=str(routing_key),
            payload=json.dumps(payload),
            properties={'headers': headers if headers else {}}
        )

    def next(self, message, payload, headers=None):
        headers = headers or message.headers or {}
        self.loop.run_until_complete(message.ack())
        index, path = message.get_current()
        if path is None or index is None:
            raise ErrorNextIsNotDefined()
        if len(message.chain) <= index + 1:
            raise ErrorNextIsNotDefined()
        message.chain[index].successful = True
        path = message.chain[index + 1]
        futures = []
        if path.isMultiple:
            if type(payload) != list:
                raise ErrorDataIsNotArray()
            for data in payload:
                futures.append(
                    self.publish_message(path.exchange, path.key, message.chain, data, headers, message.config)
                )
        else:
            futures.append(
                self.publish_message(path.exchange, path.key, message.chain, payload, headers, message.config)
            )
        self.loop.run_until_complete(asyncio.gather(*futures))
        return self

    def __get_callback(self, callback):
        async def fn(channel, body, envelope, properties):
            self.logger.info("receive message %r" % (body,))
            return callback(Message(channel, body, envelope, properties))
        return fn
