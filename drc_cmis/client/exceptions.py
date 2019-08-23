class DMSException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message


class DocumentExistsError(DMSException):
    pass


class DocumentDoesNotExistError(DMSException):
    pass


class DocumentConflictException(DMSException):
    pass


class DocumentLockedException(DMSException):
    pass


class GetFirstException(Exception):
    pass
