import md5
import os
import pprint
import time
import unittest

try:
    import settings
except ImportError:
    print "-- You haven't created the necessary settings module, please check " \
        "the documentation."
    raise

try:
    mysettings = settings.Settings()
except NameError:
    print "-- You haven't created the necessary Settings class, please check " \
        "the documentation."
    raise


class PiwikAPITestCase(unittest.TestCase):
    """
    The base class for all test classes

    Provides a fake request, PiwikTracker and PiwikTrackerEcommerce instances.
    """
    def setUp(self):
        self.settings = settings.Settings()

    def debug(self, value):
        """
        Just a debug helper

        :param value: The value to pretty print
        :type value: anything you like
        :rtype: None
        """
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(value)

    def get_random_string(self):
        """
        Return a random string

        :param length: Length
        :type length: inte
        :rtype: str
        """
        return md5.new(os.urandom(500)).hexdigest()

    def get_unique_string(self, length=20):
        epoch = str(time.time())
        epoch += self.get_random_string()
        return epoch[:length]
