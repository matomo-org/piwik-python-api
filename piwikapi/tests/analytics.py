import json
from PIL import Image
from StringIO import StringIO

from base import PiwikAPITestCase
from piwikapi.analytics import PiwikAnalytics


class AnalyticsBaseTestCase(PiwikAPITestCase):
    def setUp(self):
        super(AnalyticsBaseTestCase, self).setUp()
        self.a = PiwikAnalytics()
        self.a.set_api_url(self.settings.PIWIK_ANALYTICS_API_URL)
        self.a.set_id_site(1)
        self.a.set_format('json')
        self.a.set_period('day')
        self.a.set_date('today')
        #a.set_filter_limit(10)
        #print '4', a.get_query_string()


class AnalyticsTestCase(AnalyticsBaseTestCase):
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


class AnalyticsLiveBaseTestCase(AnalyticsBaseTestCase):
    def setUp(self):
        super(AnalyticsLiveBaseTestCase, self).setUp()
        self.a = PiwikAnalytics()
        self.a.set_api_url(self.settings.PIWIK_ANALYTICS_API_URL)
        self.a.set_id_site(1)
        self.a.set_format('json')


class AnalyticsLiveTestCase(AnalyticsLiveBaseTestCase):
    def test_live_counters(self):
        self.a.set_method('Live.getCounters')
        self.a.set_parameter('lastMinutes', 1)
        r = json.loads(self.a.send_request())
        self.assertTrue(True) # TODO
        #self.debug(r)

    def test_live_last_visits(self):
        self.a.set_method('Live.getLastVisitsDetails')
        self.a.set_parameter('lastMinutes', 1)
        visits = json.loads(self.a.send_request())
        self.assertTrue(True) # TODO
        #for visit in visits:
        #    print 'referrer url', visit['referrerUrl']
        #for x in r:
        #    print type(x)
        #self.debug(r)
