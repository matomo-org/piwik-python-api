import json
import pprint
import unittest
from PIL import Image
from StringIO import StringIO

from piwikapi.analytics import PiwikAnalytics

try:
    from piwikapi.tests.settings import Settings
    settings = Settings()
except:
    raise Exception("You haven't created the necessary Settings class in"
                    "the settings module. This is necessary to run the"
                    "unit tests, please check the documentation.")


class AnalyticsBaseTestCase(unittest.TestCase):
    def debug(self, value):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(value)


class AnalyticsTestCase(AnalyticsBaseTestCase):
    def setUp(self):
        self.a = PiwikAnalytics()
        self.a.set_api_url(settings.PIWIK_ANALYTICS_API_URL)
        self.a.set_id_site(1)
        self.a.set_format('json')
        self.a.set_period('day')
        self.a.set_date('today')
        #a.set_filter_limit(10)
        #print '4', a.get_query_string()

    def test_get_referer_sites(self):
        self.a.set_method('Referers.getWebsites')
        r = json.loads(self.a.send_request())
        #self.debug(r)

    def test_get_imagegraph(self):
        "Just a basic test to see if we get an image"
        self.a.set_method('ImageGraph.get')
        self.a.set_parameter('apiModule', 'UserCountry')
        self.a.set_parameter('apiAction', 'getCountry')
        r = self.a.send_request()
        try:
            im = Image.open(StringIO(r))
            got_image = True
        except:
            got_image = False
        self.assertTrue(
            got_image,
            "Couldn't get an ImageGraph"
        )
        #self.assertTrue(False)


class AnalyticsLiveTestCase(AnalyticsBaseTestCase):
    def setUp(self):
        self.a = PiwikAnalytics()
        self.a.set_api_url(settings.PIWIK_ANALYTICS_API_URL)
        self.a.set_id_site(1)
        self.a.set_format('json')

    def test_live_counters(self):
        self.a.set_method('Live.getCounters')
        self.a.set_parameter('lastMinutes', 1)
        r = json.loads(self.a.send_request())
        #self.debug(r)
