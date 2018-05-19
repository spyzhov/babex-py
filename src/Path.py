
class Path(object):
    """
    Path (chain item) - path to the service
    """
    def __init__(self, item):
        self.successful = bool(item.successful)
        self.isMultiple = bool(item.isMultiple)
        self.exchange = str(item.exchange)
        self.key = str(item.key)
