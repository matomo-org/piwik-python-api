import datetime
import pprint
import random
import unittest

from piwikapi.tracking import PiwikTracker

from request import FakeRequest

try:
    from settings import Settings
    settings = Settings()
except:
    raise Exception("You haven't created the necessary Settings class in"
                    "the settings module. This is necessary to run the"
                    "unit tests, please check the documentation.")


class PiwikAPITestCase(unittest.TestCase):
    """
    The base class for all test classes

    Provides a fake request, PiwikTracker and PiwikTrackerEcommerce instances.
    """
    def setUp(self):
        headers = {
            'HTTP_USER_AGENT': 'Iceweasel Gecko Linux',
            'HTTP_REFERER': 'http://referer.example.com/referer/',
            'REMOTE_ADDR': self.random_ip(),
            'HTTP_ACCEPT_LANGUAGE': 'en-us',
            'QUERY_STRING': 'a=moo&b=foo&c=quoo',
            'PATH_INFO': '/path/info/',
            'SERVER_NAME': 'action.example.com',
            'HTTPS': '',
        }
        self.settings = Settings()
        self.request = FakeRequest(headers)
        # Standard tracker
        self.pt = PiwikTracker(settings.PIWIK_SITE_ID, self.request)
        self.pt.set_api_url(settings.PIWIK_TRACKING_API_URL)

    def get_title(self, title):
        """
        Adds a timestamp to the action title"

        :param title: Action
        :type title: str
        :rtype: str
        """
        now = datetime.datetime.now()
        return "%s %d:%d:%d" % (title, now.hour, now.minute, now.second)

    def random_ip(self):
        """
        Returns an IP out of the test networks, see RFC 5735. Seemed to make
        sense to use such addresses for unit tests.

        :rtype: str
        """
        test_networks = (
            '192.0.2',
            '198.51.100',
            '203.0.113',
        )
        return '%s.%d' % (
            test_networks[random.randint(0, len(test_networks) - 1)],
            random.randint(1, 254),
        )

    def debug(self, value):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(value)
