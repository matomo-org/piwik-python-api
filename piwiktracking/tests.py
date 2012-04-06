import cgi
import unittest
import re
from datetime import datetime
from random import randint

from piwik_tracker import PiwikTracker


try:
    from django.conf import settings
    settings.PIWIK_SITE_ID
except ImportError:
    try:
        from fake_settings import FakeSettings
        settings = FakeSettings()
    except ImportError:
        raise Exception("You don't seem to be running Django or haven't"
            "configured it. Please check the readme and the unit test"
            "docs and create fake settings.")


class FakeRequest:
    """
    A replacement for Django's Request object. This is only used for unit
    tests at the moment. If you're not using Django and need to create such
    a class have a look at the source for the unit tests in tests.py.
    """
    #: Boolean, if the connection is secured or not
    secure = False

    #: HTTP headers like in the PHP $_SERVER variable, see
    #: http://php.net/manual/en/reserved.variables.server.php
    META = {}
    def __init__(self, headers):
        """
        Configure request object according to the headers we get

        Args:

        headers -- see META
        """
        self.META = headers
        if self.META['HTTPS']:
            self.secure = True # TODO test this..

    def is_secure(self):
        """
        Returns a boolean, if the connection is secured
        """
        return self.secure


class TestPiwikTrackerAPI(unittest.TestCase):
    def setUp(self):
        headers = {
            'HTTP_USER_AGENT': 'Iceweasel Gecko Linux',
            'HTTP_REFERER': 'http://referer.example.com/referer/',
            'REMOTE_ADDR': '192.0.2.4',
            'HTTP_ACCEPT_LANGUAGE': 'en-us',
            'QUERY_STRING': 'a=moo&b=foo&c=quoo',
            'PATH_INFO': '/path/info/',
            'SERVER_NAME': 'action.example.com',
            'HTTPS': '',
        }
        self.request = FakeRequest(headers)
        self.pt = PiwikTracker(settings.PIWIK_SITE_ID, self.request)
        self.pt.set_api_url(settings.PIWIK_API_URL)

    def get_title(self, title):
        now = datetime.now()
        return "%s %d:%d:%d" % (title, now.hour, now.minute, now.second)

    def random_ip(self):
        """
        Not sure if using the test networks is correct, but no part of the
        code has complained yet. See RFC 5735.
        """
        test_networks = (
            '192.0.2',
            '198.51.100',
            '203.0.113',
        )
        return '%s.%d' % (
            test_networks[randint(0, len(test_networks) - 1)],
            randint(1, 254),
        )

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
        This test can't fail we use IPs from testing networks
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
        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)
        r = self.pt.do_track_page_view(
            self.get_title('test title auth test')
        )
        self.assertRegexpMatches(
            r,
            'token_auth is authenticated',
            'We are not authenticated!',
        )

    def test_ip_changed_after_auth(self):
        """
        This is a little unexpected. Piwik accepts the incorrect IP from the
        request simply because the auth token is passed.
        """
        ip = self.request.META['REMOTE_ADDR']
        title = self.get_title('test ip (auth) %s' % ip)
        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)

        r = self.pt.do_track_page_view(title)
        self.assertRegexpMatches(
            r,
            "(Visit is known|New Visit) \(IP = %s\)" % ip,
            "IP is different from the request IP, expected %s" % ip
        )

    def test_setting_ip_works_for_authed_user_only(self):
        ip = self.random_ip()
        self.pt.set_ip(ip)
        title = self.get_title('test force ip %s ' % ip)

        r = self.pt.do_track_page_view(title)
        self.assertNotRegexpMatches(
            r,
            "(Visit is known|New Visit) \(IP = %s\)" % ip,
            "IP is the one we set, but we're not authenticated. Could be "
                "a random error..."
        )

        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)
        r = self.pt.do_track_page_view(title)
        self.assertRegexpMatches(
            r,
            "(Visit is known|New Visit) \(IP = %s\)" % ip,
            "IP not the one we set, expected %s. Could be random error..." % ip
        )

    def test_browser_has_cookies(self):
        """
        TODO can't verify
        """
        self.pt.set_browser_has_cookies()
        cookie = "piwiktrackingtest=yes; hascookies=yes"
        self.pt._set_request_cookie(cookie)
        self.assertTrue(True) # FIXME

    def test_set_resolution(self):
        """
        TODO can't verify
        """
        # verify hack
        self.pt.set_browser_has_cookies()
        self.pt.set_ip(self.random_ip())
        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)
        # verify hack
        self.pt.set_resolution(5760, 1080)
        r = self.pt.do_track_page_view('cookie test')
        self.assertTrue(True) # FIXME


if __name__ == '__main__':
    unittest.main()
