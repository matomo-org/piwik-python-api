import imghdr
try:
    import json
except ImportError:
    import simplejson as json

from piwikapi.exceptions import ConfigurationError
from piwikapi.analytics import PiwikAnalytics

from base import PiwikAPITestCase


class AnalyticsBaseTestCase(PiwikAPITestCase):
    def setUp(self):
        """
        Set up a PiwikAnalytics instance
        """
        super(AnalyticsBaseTestCase, self).setUp()
        self.a = PiwikAnalytics()
        self.a.set_api_url(self.settings['PIWIK_ANALYTICS_API_URL'])
        self.a.set_id_site(self.settings['PIWIK_SITE_ID'])
        self.a.set_format('json')
        self.a.set_period('day')
        self.a.set_date('today')


class AnalyticsClassTestCase(PiwikAPITestCase):
    """
    PiwikAnalytics tests without Piwik interaction
    """
    def test_missing_api_url(self):
        try:
            a = PiwikAnalytics()
            r = json.loads(a.send_request())
            invalid_config = True
        except ConfigurationError:
            invalid_config = False
        self.assertFalse(invalid_config)


class AnalyticsTestCase(AnalyticsBaseTestCase):
    """
    Generic analytics API tests
    """
    def _test_get_referer_sites(self):
        self.a.set_method('Referers.getWebsites')
        r = json.loads(self.a.send_request())
        #self.debug(r)
        # TODO

    def test_get_imagegraph(self):
        """
        Just a basic test to see if we can get an image
        """
        self.a.set_method('ImageGraph.get')
        self.a.set_parameter('apiModule', 'UserCountry')
        self.a.set_parameter('apiAction', 'getCountry')
        self.a.set_parameter('token_auth', self.settings['PIWIK_TOKEN_AUTH'])
        r = self.a.send_request()
        self.assertEqual(
            'png',
            imghdr.what(None, r),
            "Couldn't get a PNG ImageGraph"
        )

    def test_remove_parameter(self):
        self.a.set_parameter('testing','TEST')
        self.assertEquals(self.a.get_parameter('testing'), "TEST")
        self.a.remove_parameter('testing')
        self.assertFalse(self.a.get_parameter('testing'))


class AnalyticsLiveTestCase(AnalyticsBaseTestCase):
    """
    Useless for now
    """
    def _test_live_counters(self):
        self.a.set_method('Live.getCounters')
        self.a.set_parameter('lastMinutes', 1)
        r = json.loads(self.a.send_request())
        self.assertTrue(True)  # TODO
        #self.debug(r)

    def _test_live_last_visits(self):
        self.a.set_method('Live.getLastVisitsDetails')
        self.a.set_parameter('lastMinutes', 1)
        visits = json.loads(self.a.send_request())
        self.assertTrue(True)  # TODO
        #for visit in visits:
        #    print 'referrer url', visit['referrerUrl']
        #for x in r:
        #    print type(x)
        #self.debug(r)

