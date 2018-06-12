class QuoteNotFoundError(Exception):
    pass


class FetchingQuoteError(Exception):
    pass


class UnknownConfigError(Exception):
    pass


class RequestTimeoutError(Exception):
    pass
