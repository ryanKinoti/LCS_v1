from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AuthenticationThrottle(AnonRateThrottle):
    """
    Limits authentication attempts for anonymous users to prevent brute force attacks.
    Default: 5 attempts per minute
    """
    rate = '5/minute'

class UserActionThrottle(UserRateThrottle):
    """
    Limits API requests for authenticated users.
    Default: 60 requests per minute
    """
    rate = '60/minute'