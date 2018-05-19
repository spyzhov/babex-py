
class ErrorNextIsNotDefined(Exception):
    def __init__(self):
        super(ErrorNextIsNotDefined, self).__init__("Next path is not set in chain")


class ErrorDataIsNotArray(Exception):
    def __init__(self):
        super(ErrorDataIsNotArray, self).__init__("Path mark as `isMultiple`, but send data is not array type")
