import babex
import logging
logging.basicConfig(level='INFO', format="%(asctime)-15s %(levelname)8s %(name)20s %(message)s")

exchange = 'math'
routing_key = 'sum'
name = 'math.sum'
address = "amqp://localhost"

service = babex.new_service(name=name, address=address, isSingle=False)
service.bind_to_exchange(exchange, routing_key)
service.listen(lambda message: service.next(message, {"c": message.data["a"] + message.data["b"]}))
