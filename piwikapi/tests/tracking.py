import cgi
import datetime
import random
import re
import unittest

from piwikapi.tracking import PiwikTracker
from piwikapi.tracking import PiwikTrackerEcommerce

from base import PiwikAPITestCase
from request import FakeRequest


class TrackerBaseTestCase(PiwikAPITestCase):
    """
    This sets up a more or less random visitor

    In every test run all tests get the same testrun custom variable.
    """
    def setUp(self):
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
        self.pt = PiwikTracker(self.settings.PIWIK_SITE_ID, self.request)
        self.pt.set_api_url(self.settings.PIWIK_TRACKING_API_URL)
        self.pt.set_custom_variable(
            1,
            'testrun',
            self.settings.PIWIK_TEST_RUN,
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
            'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20100101 Firefox/11.0',
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
        except Exception:
            incorrect_id_allowed = False
        self.assertFalse(
            incorrect_id_allowed,
            "Could set an incorrect ID, %s" % incorrect_id
        )

        correct_id = self.pt.get_random_visitor_id()
        try:
            self.pt.set_visitor_id(correct_id)
            correct_id_allowed = True
        except Exception:
            correct_id_allowed = False
        self.assertTrue(
            correct_id_allowed,
            "Could not set a correct ID, %s" % incorrect_id
        )

    def test_set_debug_string_append(self):
        suffix = 'suffix'
        self.pt.set_debug_string_append(suffix)
        query_url = self.pt.get_request('foo')
        self.assertRegexpMatches(
            query_url,
            "%s$" % suffix,
            "Suffix not appended to query URL: %s" % query_url,
        )

    def test_custom_variables_invalid(self):
        value = 'bar'
        try:
            saved = self.pt.set_custom_variable('a', 'foo', value, 'page')
            illegal_id = True
        except Exception:
            illegal_id = False
        self.assertFalse(
            illegal_id,
            "No exception for trying to use an illegal ID"
        )

        try:
            saved = self.pt.set_custom_variable(1, 'foo', value, 'foo')
            illegal_scope = True
        except Exception:
            illegal_scope = False
        self.assertFalse(
            illegal_scope,
            "No exception for trying to use an illegal scope"
        )

    def test_custom_variables(self):
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


class TrackerTestCase(TrackerBaseTestCase):
    """
    Basic tracker tests

    These tests make sure that the tracking info we send is recognized by
    Piwik.
    """
    def test_default_action_title_is_correct(self):
        action_title = self.get_title('test default action title')
        r = self.pt.do_track_page_view(action_title)
        self.assertRegexpMatches(
            r,
            re.escape(action_title),
            "Action title not found, expected %s" % action_title
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
        self.pt.set_token_auth(self.settings.PIWIK_TOKEN_AUTH)
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
        self.pt.set_token_auth(self.settings.PIWIK_TOKEN_AUTH)

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

        self.pt.set_token_auth(self.settings.PIWIK_TOKEN_AUTH)
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
            "Random visitor ID found in response..." # TODO random failure
        )

        id = self.pt.get_random_visitor_id()
        self.pt.set_visitor_id(id)
        self.pt.set_token_auth(self.settings.PIWIK_TOKEN_AUTH)
        r = self.pt.do_track_page_view(self.get_title('visitor id with auth'))
        self.assertRegexpMatches(
            r,
            'Matching visitors with: visitorId=%s' % id,
            "Visitor ID not found in response"
        )
