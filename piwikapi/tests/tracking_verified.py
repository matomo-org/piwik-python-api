import json

from tracking import TrackerBaseTestCase
from analytics import AnalyticsLiveBaseTestCase

from piwikapi.analytics import PiwikAnalytics


class TrackerVerifyBaseTestCase(TrackerBaseTestCase, AnalyticsLiveBaseTestCase):
    def setUp(self):
        super(TrackerVerifyBaseTestCase, self).setUp()
        self.segment = self.get_random_string()
        self.pt.set_custom_variable(
            5,
            'testsegment',
            self.segment,
        )
        self.pt.set_token_auth(self.settings.PIWIK_TOKEN_AUTH) # verify hack
        self.pt.set_ip(self.get_random_ip())

        # Set up the analytics query
        super(AnalyticsLiveBaseTestCase, self).setUp()
        self.a.set_method('Live.getLastVisitsDetails')
        # Assume no test takes more than one minute
        self.a.set_parameter('lastMinutes', 1)
        self.a.set_segment("customVariableName5==testsegment;"
            "customVariableValue5==%s" % self.segment)

    def get_v(self, key):
        try:
            data = json.loads(self.a.send_request())[0]
        except IndexError:
            print "Request apparently not logged!"
            raise
        try:
            return data[key]
        except KeyError:
            self.debug(data)
            raise

    def get_av(self, key):
        try:
            data = json.loads(self.a.send_request())[0]['actionDetails'][0]
        except IndexError:
            print "Request apparently not logged!"
            raise
        try:
            return data[key]
        except KeyError:
            self.debug(data)
            raise


class TrackerVerifyTestCase(TrackerVerifyBaseTestCase):
    """
    Here are test we don't verify programmatically yet. I guess we'd have to
    access the Piwik API to fetch data to verify the tracking requests were
    processed properly. At the moment I only check this manually in my Piwik
    dev installation.
    """
    #def test_browser_has_cookies(self):
    #    self.pt.set_browser_has_cookies()
    #    cookie = "piwiktrackingtest=yes; hascookies=yes"
    #    self.pt._set_request_cookie(cookie)
    #    r = self.pt.do_track_page_view(self.get_title('verify browser cookie'))
    #    self.assertTrue(True) # FIXME
    #    #self.get_v('cookie', True)

    def test_set_visitor_feature_resolution(self):
        self.pt.set_resolution(5760, 1080)
        r = self.pt.do_track_page_view(self.get_title('verify resolution'))
        self.assertEqual(
            '5760x1080',
            self.get_v('resolution'),
            "Unexpected resolution value %s" % self.get_v('resolution'),
        )

    def test_set_visitor_feature_single_plugin(self):
        self.pt.set_plugins(
            flash = True,
        )
        r = self.pt.do_track_page_view(self.get_title('verify flash'))
        self.assertEqual(
            'flash',
            self.get_v('plugins'),
            "Unexpected plugins value %s" % self.get_v('plugins'),
        )

    def test_set_visitor_feature_plugins(self):
        self.pt.set_plugins(
            flash = True,
            java = True,
        )
        r = self.pt.do_track_page_view(self.get_title('verify flash + java'))
        self.assertEqual(
            'flash, java',
            self.get_v('plugins'),
            "Unexpected plugins value %s" % self.get_v('plugins'),
        )

    def test_track_goal_conversion(self):
        """
        This unit test will only work if a goal with ID=1 exists
        """
        r = self.pt.do_track_goal(1, 23)
        data = json.loads(self.a.send_request())[0]
        self.assertEqual(
            1,
            self.get_v('goalConversions'),
            "Unexpected goalConversions value %s" %
                self.get_v('goalConversions'),
        )
        # The revenue is not in the live data, but it's recorded...
        #self.assertEqual(
        #    23,
        #    self.get_av('revenue'),
        #    "Unexpected revenue value %s" % self.get_av('revenue'),
        #)



    # Browser language doesn't seem to be logged explicitly
    #def test_set_browser_language(self):
    #    language = 'de-de'
    #    self.pt.set_browser_language(language)
    #    self.assertEqual(
    #        language,
    #        self.pt.accept_language,
    #        "Browser language was not set to %s" % language
    #    )
    #    r = self.pt.do_track_page_view(self.get_title('verify browser language'))
    #    print r
    #    self.assertEqual(
    #        language,
    #        self.get_v('language'),
    #        "Unexpected value %s" % self.get_v('language'),
    #    )

    # UA string not logged
    #def test_set_user_agent(self):
    #    ua = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.24)' \
    #        'Gecko/20111103 Firefox/3.6.24'
    #    self.pt.set_user_agent(ua)
    #    self.assertEqual(
    #        ua,
    #        self.pt.user_agent,
    #        "User Agent was not set to %s" % ua
    #    )
    #    r = self.pt.do_track_page_view(self.get_title('verify user agent'))
    #    self.assertTrue(True) # FIXME
    #    #print self.segment

    #def test_custom_variables(self):
    #    action_title = self.get_title('verify custom var')
    #    r = self.pt.do_track_page_view(action_title)
    #    self.assertTrue(True) # FIXME
    #    #print self.segment

    #    ##c = Client()
    #    #url = self.pt.get_request(self.settings.PIWIK_SITE_ID)
    #    ##print url
    #    #value = 'quoo'
    #    #self.pt.set_custom_variable(1, 'foo', value, 'visit')
    #    #saved = self.pt.get_custom_variable(1, 'visit')
    #    #self.assertEqual(
    #    #    value,
    #    #    saved[1],
    #    #    "Custom visit variable was not saved, got %s" % saved[1],
    #    #)

    #    #print r
