class NoTableException(BaseException):
    def __init__(self, message):
        """
        The given table is missing

        :param message: output message
        """
        super(NoTableException, self).__init__(message)

