import cgi
import datetime
import random
import re
import sys
try:
    import json
except ImportError:
    import simplejson as json
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from piwikapi.analytics import PiwikAnalytics
from piwikapi.exceptions import InvalidParameter
from piwikapi.exceptions import ConfigurationError
from piwikapi.tracking import PiwikTracker
from piwikapi.tracking import PiwikTrackerEcommerce

from analytics import AnalyticsBaseTestCase
from base import PiwikAPITestCase
from request import FakeRequest


class TrackerBaseTestCase(PiwikAPITestCase):
    """
    This sets up a more or less random visitor

    In every test run all tests get the same testrun custom variable.
    """
    def setUp(self):
        """
        Set up a PiwikTracker instance
        """
        super(TrackerBaseTestCase, self).setUp()
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
        self.request = FakeRequest(headers)
        self.pt = PiwikTracker(self.settings['PIWIK_SITE_ID'], self.request)
        self.pt.set_api_url(self.settings['PIWIK_TRACKING_API_URL'])
        self.pt.set_custom_variable(
            1,
            'testrun',
            self.get_unique_string(),
        )

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

        Only return Desktop UAs as Piwik doesn't like big resolutions on
        devices it thinks are mobile.

        :rtype: string
        """
        uas = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like "
                "Gecko) Chrome/17.0.963.83 Safari/535.11",
            'Mozilla/5.0 (X11; Linux x86_64; rv:10.0.3) Gecko/20100101 ',
                'Firefox/10.0.3 Iceweasel/10.0.3',
            'Opera/9.80 (Windows NT 6.1; WOW64; U; de) Presto/2.10.229 '
                'Version/11.62',
            'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20100101 '
                'Firefox/11.0',
            #'Mozilla/5.0 (iPad; U; CPU iPhone OS 5_1 like Mac OS X; de_DE) '
            #    'AppleWebKit (KHTML, like Gecko) Mobile [FBAN/FBForIPhone;'
            #    'FBAV/4.1.1;FBBV/4110.0;FBDV/iPad2,1;FBMD/iPad;FBSN/iPhone '
            #    'OS;FBSV/5.1;FBSS/1; FBCR/;FBID/tablet;FBLC/de_DE;FBSF/1.0]',
            #'Mozilla/5.0 (Linux; U; Android 2.3.6; fr-fr; GT-N7000 Build/'
            #    'GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) '
            #    'Version/4.0 Mobile Safari/533.1',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; de-de) '
                'AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 '
                'Safari/533.18.5',
        )
        return self.get_random(uas)

    def get_random_language(self):
        """
        Return a random language code
        """
        langs = (
            'ar-EG',
            'ar-TN',
            'de',
            'en',
            'en-GB',
            'en-US',
            'es',
            'es-AR',
            'fr',
            'in',
            'it',
            'jp',
            'ms',
            'pl',
            'pt',
            'pt-BR',
            'ru',
            'tn',
            'zh-TW',
            'zh-CN',
        )
        return self.get_random(langs)


class TrackerClassTestCase(TrackerBaseTestCase):
    """
    PiwikTracker tests, without Piwik interaction
    """
    def test_set_visitor_id(self):
        """
        This is a little sloppy, we should probably create a custom exception
        """
        incorrect_id = 'asdf'
        try:
            self.pt.set_visitor_id(incorrect_id)
            incorrect_id_allowed = True
        except InvalidParameter:
            incorrect_id_allowed = False
        self.assertFalse(
            incorrect_id_allowed,
            "Could set an incorrect ID, %s" % incorrect_id
        )

        correct_id = self.pt.get_random_visitor_id()
        try:
            self.pt.set_visitor_id(correct_id)
            correct_id_allowed = True
        except InvalidParameter:
            correct_id_allowed = False
        self.assertTrue(
            correct_id_allowed,
            "Could not set a correct ID, %s" % incorrect_id
        )

    def test_set_debug_string_append(self):
        suffix = 'suffix'
        self.pt.set_debug_string_append(suffix)
        query_url = self.pt._get_request('foo')
        self.assertRegexpMatches(
            query_url,
            "%s$" % suffix,
            "Suffix not appended to query URL: %s" % query_url,
        )

    def test_incorrect_custom_variables_invalid(self):
        value = 'bar'
        try:
            saved = self.pt.set_custom_variable('a', 'foo', value, 'page')
            invalid_id = True
        except InvalidParameter:
            invalid_id = False
        self.assertFalse(
            invalid_id,
            "No exception for trying to use an illegal ID"
        )

        try:
            saved = self.pt.set_custom_variable(1, 'foo', value, 'foo')
            invalid_scope = True
        except InvalidParameter:
            invalid_scope = False
        self.assertFalse(
            invalid_scope,
            "No exception for trying to use an illegal scope"
        )

    def test_set_custom_variables(self):
        value = 'quoo'
        self.pt.set_custom_variable(1, 'foo', value, 'page')
        saved = self.pt.get_custom_variable(1, 'page')
        self.assertEqual(
            value,
            saved[1],
            "Custom page variable was not saved, got %s" % saved[1],
        )

    def test_set_user_agent(self):
        ua = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.24)' \
            'Gecko/20111103 Firefox/3.6.24'
        self.pt.set_user_agent(ua)
        self.assertEqual(
            ua,
            self.pt.user_agent,
            "User Agent was not set to %s" % ua
        )

    def test_set_visitor_id_exception(self):
        try:
            vid = self.get_random_string()
            vid = vid[:self.pt.LENGTH_VISITOR_ID + 1]
            self.pt.set_visitor_id(vid)
            invalid_value = True
        except InvalidParameter:
            invalid_value = False
        self.assertFalse(invalid_value)

    def test_do_track_action_exception(self):
        """
        Should probably also test that valid parameters pass
        """
        try:
            action = 'foo'
            self.pt.do_track_action('/', action)
            invalid_value = True
        except InvalidParameter:
            invalid_value = False
        self.assertFalse(invalid_value)

    def test_set_custom_variable_exception(self):
        try:
            id = 'foo'
            self.pt.set_custom_variable(id, 'foo', 'bar')
            invalid_value = True
        except InvalidParameter:
            invalid_value = False
        self.assertFalse(invalid_value)

    def test_set_custom_variable_scope_exception(self):
        try:
            scope = 'foo'
            self.pt.set_custom_variable(1, 'foo', 'bar', scope)
            invalid_value = True
        except InvalidParameter:
            invalid_value = False
        self.assertFalse(invalid_value)

    def test_get_custom_variable_exception(self):
        try:
            id = 'foo'
            self.pt.get_custom_variable(id)
            invalid_value = True
        except InvalidParameter:
            invalid_value = False
        self.assertFalse(invalid_value)

    def test_get_custom_variable_scope_exception(self):
        try:
            scope = 'foo'
            self.pt.get_custom_variable(1, scope)
            invalid_value = True
        except InvalidParameter:
            invalid_value = False
        self.assertFalse(invalid_value)

    def test_missing_api_url(self):
        try:
            pt = PiwikTracker(self.settings['PIWIK_SITE_ID'], self.request)
            pt.do_track_page_view('fake title')
            invalid_config = True
        except ConfigurationError:
            invalid_config = False
        self.assertFalse(invalid_config)

    def test_unknown_set_plugins(self):
        try:
            self.pt.set_plugins(
                unknown=True,
            )
            invalid_plugin = True
        except ConfigurationError:
            invalid_plugin = False
        self.assertFalse(invalid_plugin)


class TrackerVerifyDebugTestCase(TrackerBaseTestCase):
    """
    These tests make sure that the tracking info we send is recognized by
    checking the debug output of Piwik.

    TODO: Use the analytics API to verify the tests.
    """
    def test_default_action_title_is_correct(self):
        action_title = self.get_title('test default action title')
        r = self.pt.do_track_page_view(action_title)
        self.assertRegexpMatches(
            r,
            re.escape(action_title),
            "Action title not found"
            #"Action title not found, expected %s" % action_title
        )

    def test_default_user_is_not_authenticated(self):
        action_title = self.get_title('test default no auth')
        r = self.pt.do_track_page_view(action_title)
        self.assertNotRegexpMatches(
            r,
            'token_auth is authenticated',
            "We are authenticated but shouldn't be",
        )

    def test_default_action_url_is_correct(self):
        action_title = self.get_title('test default action url')
        r = self.pt.do_track_page_view(action_title)
        url = 'Action URL = http://%s%s?%s' % (
            self.request.META.get('SERVER_NAME'),
            self.request.META.get('PATH_INFO'),
            cgi.escape(self.request.META['QUERY_STRING']),
        )
        self.assertRegexpMatches(
            r,
            re.escape(url),
            "Action URL not found, expected %s" % url
        )

    def test_default_ip_is_not_changed(self):
        """
        This test can't fail, we use IPs from testing networks
        """
        ip = self.request.META['REMOTE_ADDR']
        title = self.get_title('test ip %s' % ip)
        r = self.pt.do_track_page_view(title)
        self.assertNotRegexpMatches(
            r,
            "(Visit is known|New Visit) \(IP = %s\)" % ip,
            "IP is different from the request IP, expected %s" % ip
        )

    def test_default_repeat_visits_recognized(self):
        action_title = self.get_title('test default repeat visit')
        r = self.pt.do_track_page_view(action_title)
        self.assertNotRegexpMatches(
            r,
            "(Visit is known|New Visit) \(IP = %s\)" %
                self.request.META['REMOTE_ADDR'],
            "IP is different from the request IP",
        )

    def test_token_auth_succeeds(self):
        self.pt.set_token_auth(self.settings['PIWIK_TOKEN_AUTH'])
        r = self.pt.do_track_page_view(
            self.get_title('test title auth test')
        )
        self.assertRegexpMatches(
            r,
            'token_auth is authenticated',
            'We are not authenticated!',
        )

    def test_ip_not_changed_after_auth(self):
        """
        I think there was a bug in my earlier code. The IP should not be set
        or overridden just because we authenticated, Piwik should log the IP
        of the host that made the tracking request.
        """
        ip = self.request.META['REMOTE_ADDR']
        title = self.get_title('test ip (auth) %s' % ip)
        self.pt.set_token_auth(self.settings['PIWIK_TOKEN_AUTH'])

        r = self.pt.do_track_page_view(title)
        self.assertNotRegexpMatches(
            r,
            "(Visit is known|New Visit) \(IP = %s\)" % ip,
            "IP is different from the request IP, expected %s" % ip
        )

    def test_setting_ip_works_for_authed_user_only(self):
        ip = self.get_random_ip()
        self.pt.set_ip(ip)
        title = self.get_title('test force ip %s ' % ip)

        r = self.pt.do_track_page_view(title)
        self.assertNotRegexpMatches(
            r,
            "(Visit is known|New Visit) \(IP = %s\)" % ip,
            "IP is the one we set, but we're not authenticated. Could be "
                "a random error..."
        )

        self.pt.set_token_auth(self.settings['PIWIK_TOKEN_AUTH'])
        r = self.pt.do_track_page_view(title)
        self.assertRegexpMatches(
            r,
            "(Visit is known|New Visit) \(IP = %s\)" % ip,
            "IP not the one we set, expected %s. Could be random error..." % ip
        )

    def test_set_visitor_id(self):
        id = self.pt.get_random_visitor_id()
        self.pt.set_visitor_id(id)
        self.assertEqual(
            self.pt.get_visitor_id(),
            id,
            "Visitor ID %s was not saved" % id
        )
        r = self.pt.do_track_page_view(self.get_title('visitor id no auth'))
        self.assertNotRegexpMatches(
            r,
            'config_id = %s' % id,
            "Random visitor ID found in response..."  # TODO random failure
        )

        id = self.pt.get_random_visitor_id()
        self.pt.set_visitor_id(id)
        self.pt.set_token_auth(self.settings['PIWIK_TOKEN_AUTH'])
        r = self.pt.do_track_page_view(self.get_title('visitor id with auth'))
        self.assertRegexpMatches(
            r,
            'Matching visitors with: visitorId=%s' % id,
            "Visitor ID not found in response"
        )


class TrackerVerifyBaseTestCase(TrackerBaseTestCase, AnalyticsBaseTestCase):
    """
    The base class for tests that use the analytics API to verify
    """
    def setUp(self):
        """
        To be able to verify against the analytics API each test gets a random
        custom variable. Segmentation is then used to query the submitted
        data.
        """
        super(TrackerVerifyBaseTestCase, self).setUp()
        self.segment = self.get_unique_string()
        self.pt.set_custom_variable(
            5,
            'testsegment',
            self.segment,
        )
        self.pt.set_token_auth(self.settings['PIWIK_TOKEN_AUTH'])  # verify hack
        self.pt.set_ip(self.get_random_ip())

        # Set up the analytics query
        super(AnalyticsBaseTestCase, self).setUp()
        self.a.set_method('Live.getLastVisitsDetails')
        # Assume no test takes more than one minute
        self.a.set_parameter('lastMinutes', 1)
        self.a.set_segment("customVariableName5==testsegment;"
            "customVariableValue5==%s" % self.segment)

    def get_v(self, key):
        """
        Get a variable from the last visit
        """
        try:
            self.a.set_parameter('token_auth', self.settings['PIWIK_TOKEN_AUTH'])
            if sys.version_info[0] >= 3:
                data = json.loads(self.a.send_request().decode('utf-8'))
            else:
                data = json.loads(self.a.send_request())
            data = data[-1]
        except IndexError:
            print("Request apparently not logged!")
            raise
        except KeyError:
            self.debug(data)
            raise
        try:
            r = data[key]
        except KeyError:
            self.debug(data)
            raise
        return r

    def get_av(self, key):
        """
        Get an action variable from the last visit
        """
        try:
            self.a.set_parameter('token_auth', self.settings['PIWIK_TOKEN_AUTH'])
            if sys.version_info[0] >= 3:
                data = json.loads(self.a.send_request().decode('utf-8'))[-1]['actionDetails'][0]
            else:
                data = json.loads(self.a.send_request())[-1]['actionDetails'][0]
        except IndexError:
            print("Request apparently not logged!")
            raise
        try:
            return data[key]
        except KeyError:
            self.debug(data)
            raise


class TrackerVerifyTestCase(TrackerVerifyBaseTestCase):
    """
    Here are test we don't verify programmatically yet.
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
            flash=True,
        )
        r = self.pt.do_track_page_view(self.get_title('verify flash'))
        self.assertEqual(
            'flash',
            self.get_v('plugins'),
            "Unexpected plugins value %s" % self.get_v('plugins'),
        )

    def test_set_visitor_feature_plugins(self):
        self.pt.set_plugins(
            flash=True,
            java=True,
        )
        r = self.pt.do_track_page_view(self.get_title('verify flash + java'))
        self.assertEqual(
            'flash, java',
            self.get_v('plugins'),
            "Unexpected plugins value %s" % self.get_v('plugins'),
        )

    def test_action_link(self):
        """
        Test out action
        """
        url = 'http://out.example.com/out/15'
        r = self.pt.do_track_action(url, 'link')
        self.a.set_parameter('token_auth', self.settings['PIWIK_TOKEN_AUTH'])
        if sys.version_info[0] >= 3:
            data = json.loads(self.a.send_request().decode('utf-8'))[0]
        else:
            data = json.loads(self.a.send_request())[0]
        self.assertEqual(
            url,
            self.get_av('url'),
            "Unexpected url value %s" % self.get_av('url'),
        )
        self.assertEqual(
            'outlink',
            self.get_av('type'),
            "Unexpected type value %s" % self.get_av('type'),
        )

    def test_action_click(self):
        """
        Test download action
        """
        url = 'http://download.example.com/download/15'
        r = self.pt.do_track_action(url, 'download')
        self.assertEqual(
            url,
            self.get_av('url'),
            "Unexpected url value %s" % self.get_av('url'),
        )
        self.assertEqual(
            'download',
            self.get_av('type'),
            "Unexpected type value %s" % self.get_av('type'),
        )

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

    def test_set_user_agent(self):
        """
        Piwik doesn't save the UA string but processes it.
        """
        ua = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.24)' \
            'Gecko/20111103 Firefox/3.6.24'
        self.pt.set_user_agent(ua)
        #self.assertEqual(
        #    ua,
        #    self.pt.user_agent,
        #    "User Agent was not set to %s" % ua
        #)
        r = self.pt.do_track_page_view(self.get_title('verify user agent'))
        self.assertEqual(
            'Windows 7',
            self.get_v('operatingSystem'),
            "Unexpected operatingSystem value %s" %
                self.get_v('operatingSystem'),
        )
        self.assertEqual(
            'Firefox 3.6',
            self.get_v('browserName'),
            "Unexpected browserName value %s" % self.get_v('browserName'),
        )
        self.assertEqual(
            'gecko',
            self.get_v('browserFamily'),
            "Unexpected browserFamily value %s" % self.get_v('browserFamily'),
        )

    #def test_get_custom_variable_from_cookie(self):
    #    r = self.pt.do_track_page_view(self.get_title('foo 1'))
    #    data = json.loads(self.a.send_request())
    #    self.debug(data)
    #    self.pt.set_url_referer('/ownpage/')
    #    r = self.pt.do_track_page_view(self.get_title('foo 2'))
    #    data = json.loads(self.a.send_request())
    #    self.debug(data)
    #    #saved = self.pt.get_custom_variable(1, 'visit')

    #def test_set_attribution_info(self):
    #    """
    #    Referer attribution information:
    #    [
    #        campaign name,
    #        campaign keyword,
    #        timestamp,
    #        raw URL,
    #    ]
    #    """
    #    r = self.pt.do_track_page_view('foobar')
    #    info = [
    #        'Campaign Name Two',
    #        'CampaignKeyword',
    #        '',
    #        'http://capaigntwo.example.com',
    #    ]
    #    info_json = json.dumps(info)
    #    self.pt.set_attribution_info(info_json)
    #    title = 'foobar'
    #    r = self.pt.do_track_page_view(title)
    #    data = json.loads(self.a.send_request())

    #    #value = 'quoo'
    #    #self.pt.set_custom_variable(1, 'foo', value, 'visit')
    #    #saved = self.pt.get_custom_variable(1, 'visit')
    #    #self.assertEqual(
    #    #    value,
    #    #    saved[1],
    #    #    "Custom visit variable was not saved, got %s" % saved[1],
    #    #)

    #    #print r
