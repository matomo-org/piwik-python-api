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
            'HTTP_USER_AGENT': self.get_random_ua(),
            'HTTP_REFERER': 'http://referer%d.example.com/referer/' %
                random.randint(0, 99),
            'REMOTE_ADDR': self.get_random_ip(),
            'HTTP_ACCEPT_LANGUAGE': self.get_random_language(),
            'QUERY_STRING': 'testrand=%d' % random.randint(0, 99),
            'PATH_INFO': '/path%d/' % random.randint(0, 99),
            'SERVER_NAME': 'action%d.example.com' % random.randint(0, 99),
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

    def get_random_ip(self):
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

    def get_random(self, choices):
        return choices[random.randint(0, len(choices) - 1)]

    def get_random_ua(self):
        """
        Returns a random user agent string

        :rtype: string
        """
        uas = (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like '
                'Gecko) Chrome/17.0.963.83 Safari/535.11',
            'Mozilla/5.0 (X11; Linux x86_64; rv:10.0.3) Gecko/20100101 ',
                'Firefox/10.0.3 Iceweasel/10.0.3',
            'Opera/9.80 (Windows NT 6.1; WOW64; U; de) Presto/2.10.229 '
                'Version/11.62',
            'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20100101 Firefox/11.0',
            'Mozilla/5.0 (iPad; U; CPU iPhone OS 5_1 like Mac OS X; de_DE) '
                'AppleWebKit (KHTML, like Gecko) Mobile [FBAN/FBForIPhone;'
                'FBAV/4.1.1;FBBV/4110.0;FBDV/iPad2,1;FBMD/iPad;FBSN/iPhone '
                'OS;FBSV/5.1;FBSS/1; FBCR/;FBID/tablet;FBLC/de_DE;FBSF/1.0]',
            'Mozilla/5.0 (Linux; U; Android 2.3.6; fr-fr; GT-N7000 Build/'
                'GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) '
                'Version/4.0 Mobile Safari/533.1',
        )
        return self.get_random(uas)

    def get_random_language(self):
        langs = (
            'de',
            'fr',
            'en-US',
            'zh-TW',
            'it',
            'pt-BR',
            'es-AR',
            'ar-tn',
        )
        return self.get_random(langs)


    def debug(self, value):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(value)
