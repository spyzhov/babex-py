import uuid
import logging
import pika
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

    def __init__(self, name, address="amqp://localhost", isSingle=True, skipDeclareQueue=False):
        self.address = address
        self.skipDeclareQueue = skipDeclareQueue
        self.queue_name = '{}.{}'.format(name, uuid.uuid4()) if isSingle else name
        self.connection = None
        self.channel = None
        self.options = {"exclusive": True, "auto_delete": True} if isSingle else {}
        super(Service, self).__init__()

    def connect(self):
        self.logger.info(f"Try to connect to {self.address}")
        self.connection = pika.BlockingConnection(pika.URLParameters(self.address))
        self.channel = self.connection.channel()
        if not self.skipDeclareQueue:
            self.channel.queue_declare(queue=self.queue_name, **self.options)
        self.logger.info(f"waiting for messages on {self.queue_name}")
        return self

    def listen(self, callback, **kwargs):
        self.channel.basic_consume(self.__get_callback(callback), queue=self.queue_name, **kwargs)
        self.channel.start_consuming()

    def bind_to_exchange(self, exchange, routing_key, **kwargs):
        self.channel.queue_bind(queue=self.queue_name, exchange=exchange, routing_key=routing_key, **kwargs)
        return self

    def prefetch(self, prefetch_count, **kwargs):
        self.channel.basic_qos(prefetch_count=prefetch_count, **kwargs)
        return self

    def publish_message(self, exchange_name, routing_key, chain=None, data=None, headers=None, config=None):
        self.logger.info(f"publish message to {exchange_name}:{routing_key}")
        chain = chain or []
        payload = {
            'data': data,
            'chain': [p.__dict__ for p in chain],
            'config': config,
        }
        self.channel.basic_publish(
            exchange=str(exchange_name),
            routing_key=str(routing_key),
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                headers=headers if headers else {}
            )
        )

    def next(self, message, payload, headers=None):
        headers = headers or message.headers or {}
        message.ack()
        index, path = message.get_current()
        if path is None or index is None:
            raise ErrorNextIsNotDefined()
        if len(message.chain) <= index + 1:
            raise ErrorNextIsNotDefined()
        message.chain[index].successful = True
        path = message.chain[index + 1]
        if path.isMultiple:
            if type(payload) != list:
                raise ErrorDataIsNotArray()
            for data in payload:
                self.publish_message(path.exchange, path.key, message.chain, data, headers, message.config)
        else:
            self.publish_message(path.exchange, path.key, message.chain, payload, headers, message.config)
        return self

    def __get_callback(self, callback):
        def fn(ch, method, properties, body):
            self.logger.info("receive message %r" % (body,))
            return callback(Message(ch, body, method, properties))
        return fn
