class FakeRequest:
    """
    A replacement for Django's Request object. This is only used for unit
    tests at the moment. If you're not using Django and need to create such
    a class have a look at the source for the tests fake request class in
    in tests/request.py
    """
    #: Boolean, if the connection is secured or not
    secure = False

    #: HTTP headers like in the PHP $_SERVER variable, see
    #: http://php.net/manual/en/reserved.variables.server.php
    META = {}

    #: Cookies... work in progress
    COOKIES = False

    def __init__(self, headers):
        """
        Configure request object according to the headers we get

        :param headers: see META
        :type headers: dict
        :rtype: None
        """
        self.META = headers
        if self.META['HTTPS']:
            self.secure = True  # TODO test this..

    def is_secure(self):
        """
        Returns a boolean, if the connection is secured

        :rtype: bool
        """
        return self.secure
