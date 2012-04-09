import json
from PIL import Image
from StringIO import StringIO

from base import PiwikAPITestCase
from piwikapi.analytics import PiwikAnalytics


class AnalyticsTestCase(PiwikAPITestCase):
    def setUp(self):
        super(AnalyticsTestCase, self).setUp()
        self.a = PiwikAnalytics()
        self.a.set_api_url(self.settings.PIWIK_ANALYTICS_API_URL)
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


class AnalyticsLiveTestCase(PiwikAPITestCase):
    def setUp(self):
        super(AnalyticsLiveTestCase, self).setUp()
        self.a = PiwikAnalytics()
        self.a.set_api_url(self.settings.PIWIK_ANALYTICS_API_URL)
        self.a.set_id_site(1)
        self.a.set_format('json')

    def test_live_counters(self):
        self.a.set_method('Live.getCounters')
        self.a.set_parameter('lastMinutes', 1)
        r = json.loads(self.a.send_request())
        #self.debug(r)
