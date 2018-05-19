from .errors import ErrorDataIsNotArray, ErrorNextIsNotDefined
from .Service import Service

ServiceConfig = {
    "name": "",
    "address": "amqp://localhost",
    "isSingle": True,
    "skipDeclareQueue": False
}


def new_service(**kwargs):
    """
    :param name:
    :param address:
    :param isSingle:
    :param skipDeclareQueue:
    :param loop:
    :return:
    """
    return Service(**kwargs).connect()
