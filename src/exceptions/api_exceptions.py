"""api error module that contains various error classes
All of the error classes defined here represents the various
api errors that can occur.
"""
from sentry_sdk import capture_exception


class ApiError(Exception):
    """The generic api error class"""
    def to_dict(self):
        """sets the message value"""
        return dict(message=self.message)


class ItemNotFoundError(ApiError):
    """Error class for when item not found"""
    status_code = 404
    capture_exception(ApiError)


class BadRequestError(ApiError):
    """Error class for when bad request is made.
     This error can be raised when our clients make
      invalid calls to our api or when our code makes
       invalid calls against clients our api is dependant on"""
    status_code = 400
    capture_exception(ApiError)
        

class ServiceNotAvailableError(ApiError):
    """Error class for when service is not available. This error is raised
    when the api clients we depend on are temporarily unavailable"""
    status_code = 503
    capture_exception(ApiError)
