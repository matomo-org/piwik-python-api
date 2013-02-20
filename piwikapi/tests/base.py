import os
import pprint
import sys
import time
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from hashlib import md5


on_rtd = os.environ.get('READTHEDOCS', None) == 'True'


class PiwikAPITestCase(unittest.TestCase):
    """
    The base class for all test classes

    Provides a fake request, PiwikTracker and PiwikTrackerEcommerce instances.
    """
    def setUp(self):
        try:
            keys = (
                'PIWIK_TRACKING_API_URL',
                'PIWIK_ANALYTICS_API_URL',
                'PIWIK_TOKEN_AUTH',
                'PIWIK_SITE_ID',
            )
            self.settings = {}
            for key in keys:
                self.settings[key] = os.environ.get(key)
            self.settings['PIWIK_GOAL_ID'] = os.environ.get('PIWIK_GOAL_ID', None)
        except:
            raise

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
        return md5(os.urandom(500)).hexdigest()

    def get_unique_string(self, length=20):
        epoch = str(time.time())
        epoch += self.get_random_string()
        return epoch[:length]

    # Python2/3 wrappers
    def assertRegexpMatches(self, text, regexp, msg):
        if sys.version_info[0] >= 3:
            self.assertRegex(text, regexp, msg)
        else:
            super(PiwikAPITestCase, self).assertRegexpMatches(text, regexp, msg)

    def assertNotRegexpMatches(self, text, regexp, msg):
        if sys.version_info[0] >= 3:
            self.assertNotRegex(text, regexp, msg)
        else:
            super(PiwikAPITestCase, self).assertNotRegexpMatches(text, regexp, msg)

    def assertEquals(self, first, second, msg=''):
        if sys.version_info[0] >= 3:
            self.assertEqual(first, second, msg)
        else:
            super(PiwikAPITestCase, self).assertEquals(first, second, msg)
