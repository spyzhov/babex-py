# About

Имплементация протокола общения между сервисами, через очередь сообщений RabbitMQ.

# Versions

## Version 1

Input message:
```
{
  "data": Any,
  "chain": [Path],
  "config": Any
}
```

Where `Path` like:
```
{
  "exchange": String,
  "key": String,
  "isMultiple": Bool,
  "successful": Bool
}
```

# Example

Service example `Sum(a, b)`:

Request:
```json
{
  "data": {
    "a": 2, 
    "b": 3
  },
  "chain": [
    {
      "exchange": "math",
      "key": "sum",
      "isMultiple": false,
      "successful": false
    },
    {
      "exchange": "math",
      "key": "sum.next",
      "isMultiple": false,
      "successful": false
    }
  ],
  "config": null
}
```

```python
import babex
exchange = 'math'
routing_key = 'sum'
name = 'math.sum'
address = "amqp://localhost"

service = babex.new_service(name=name, address=address)
service.bind_to_exchange(exchange, routing_key)
service.listen(lambda message: service.next(message, {"c": message.data["a"] + message.data["b"]}))

```

Result:
```json
{
  "data": {
    "c": 5
  },
  "chain": [
    {
      "exchange": "math",
      "key": "sum",
      "isMultiple": false,
      "successful": true
    },
    {
      "exchange": "math",
      "key": "sum.next",
      "isMultiple": false,
      "successful": false
    }
  ],
  "config": null
}
```