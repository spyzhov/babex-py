
class Path(object):
    """
    Path (chain item) - path to the service
    """
    def __init__(self, item):
        self.successful = bool(item.get('successful'))
        self.isMultiple = bool(item.get('isMultiple'))
        self.exchange = str(item.get('exchange'))
        self.key = str(item.get('key'))
