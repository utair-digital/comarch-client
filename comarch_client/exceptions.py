"""Comarch exceptions"""


class BaseError(Exception):

    http_code = None
    error_code = None
    message = None
    internal_message = None

    def __init__(self, message=None, error_code=None, http_code=None, internal_message=None):
        """
        :param message:
        :param error_code:
        :param http_code:
        :param internal_message:
        """
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        self.http_code = http_code or self.http_code
        self.internal_message = internal_message or self.internal_message

        assert self.message, "Message not implemented!"
        assert self.error_code, "Error code not implemented!"
        assert self.http_code, "Http code not implemented!"

        super(BaseError, self).__init__(message)

    def __str__(self):
        base = "{}:{}: {}".format(self.http_code, self.error_code, self.message,)
        if self.internal_message:
            return "{0} {{{1}}}".format(base, self.internal_message)
        return base


class ComarchError(BaseError):
    """Base comarch error"""
    pass


class ComarchConnectionError(ComarchError):
    """Comarch connection error"""

    http_code = 503
    error_code = 50301
    message = "Bonus program is unavailable"
