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
    A replacement for Django's Request object, used for unit tests
    """
    META = {
        'HTTP_USER_AGENT': 'Iceweasel Gecko Linux',
        'HTTP_REFERER': 'http://referer.example.com/referer/',
        'REMOTE_ADDR': '192.0.2.4',
        'HTTP_ACCEPT_LANGUAGE': 'en-us',
        'QUERY_STRING': 'a=moo&b=foo&c=quoo',
    }
    secure = False
    host = 'action.example.com'
    path_info = '/path/info/'

    def is_secure(self):
        return self.secure

    def get_host(self):
        return self.host


class TestPiwikTrackerAPI(unittest.TestCase):
    def setUp(self):
        self.request = FakeRequest()
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
            self.request.host,
            self.request.path_info,
            cgi.escape(self.request.META['QUERY_STRING']),
        )
        self.assertRegexpMatches(
            r,
            re.escape(url),
            "Action URL not found, expected %s" % url
        )

    def test_default_ip_is_not_changed(self):
        """
        This test could fail because the request object has the same IP
        as your box... TODO
        """
        ip = self.request.META['REMOTE_ADDR']
        title = self.get_title('test ip %s' % ip)
        r = self.pt.do_track_page_view(title)
        self.assertNotRegexpMatches(
            r,
            "Visit is known \(IP = %s\)" % ip,
            "IP is different from the request IP, expected %s" % ip
        )

    def test_default_repeat_visits_recognized(self):
        action_title = self.get_title('test default repeat visit')
        r = self.pt.do_track_page_view(action_title)
        # We need a second request in case this test is run from a new IP
        r = self.pt.do_track_page_view('%s - second' % action_title)
        self.assertNotRegexpMatches(
            r,
            "New Visit \(IP = %s\)" % self.request.META['REMOTE_ADDR'],
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
        request. TODO look into this...
        """
        ip = self.request.META['REMOTE_ADDR']
        title = self.get_title('test ip (auth) %s' % ip)
        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)

        # We need a second request in case this test is run from a new IP
        r = self.pt.do_track_page_view(title)
        r = self.pt.do_track_page_view(title)
        self.assertRegexpMatches(
            r,
            "Visit is known \(IP = %s\)" % ip,
            "IP is different from the request IP, expected %s" % ip
        )

    def test_setting_ip_works_for_authed_user_only(self):
        """
        Well... this unit test could fail randomly if the same random IP is
        chosen again... TODO
        """
        ip = self.random_ip()
        self.pt.set_ip(ip)
        title = self.get_title('test force ip %s ' % ip)

        r = self.pt.do_track_page_view(title)
        self.assertNotRegexpMatches(
            r,
            "New Visit \(IP = %s\)" % ip,
            "IP is the one we set, but we're not authenticated. Could be "
                "a random error..."
        )

        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)
        r = self.pt.do_track_page_view(title)
        self.assertRegexpMatches(
            r,
            "New Visit \(IP = %s\)" % ip,
            "IP not the one we set, expected %s. Could be random error..." % ip
        )


if __name__ == '__main__':
    unittest.main()
