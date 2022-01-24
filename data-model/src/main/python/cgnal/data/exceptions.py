class NoTableException(BaseException):
    def __init__(self, message: str) -> None:
        """
        The given table is missing

        :param message: output message
        """
        super(NoTableException, self).__init__(message)
