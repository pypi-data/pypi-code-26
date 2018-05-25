class UnsplashBaseError(Exception):
    pass


class UnsplashAuthError(UnsplashBaseError):

    def __init__(self, reason, **kwargs):
        self.reason = reason
        self.message = "Unsplash Authentication Error: %s " % self.reason
        super(UnsplashAuthError, self).__init__(message=self.message, **kwargs)


class UnsplashRateLimitError(UnsplashBaseError):
    pass


class UnsplashError(UnsplashBaseError):
    pass


class UnsplashConnectionError(UnsplashBaseError):
    pass
