import cgi
import unittest
import re
from datetime import datetime
from random import randint

from django.conf import settings

from piwiktracker import PiwikTracker


class FakeRequest(object):
    META = {
        'HTTP_USER_AGENT': 'Iceweasel Gecko Linux',
        'HTTP_REFERER': 'http://referer.example.com/referer/',
        'REMOTE_ADDR': '112.34.56.78',
        'HTTP_ACCEPT_LANGUAGE': 'en-us',
        'QUERY_STRING': 'a=moo&b=foo&c=quoo',
    }
    host = 'action.example.com'
    secure = False
    path_info = '/path/info/'

    def is_secure(self):
        return self.secure

    def get_host(self):
        return self.host


class TestPiwikTrackerAPI(unittest.TestCase):
    def setUp(self):
        self.request = FakeRequest()
        self.pt = PiwikTracker(1, self.request)
        self.pt.set_api_url(settings.PIWIK_API_URL)

    def get_title(self, title):
        now = datetime.now()
        return "%s %d:%d:%d" % (title, now.hour, now.minute, now.second)

    def random_ip(self):
        return '%d.%d.%d.%d' % (
            randint(1, 255),
            randint(1, 255),
            randint(1, 255),
            randint(1, 255),
        )

    def test_defaults(self):
        action_title = self.get_title('test title no auth test')
        r = self.pt.do_track_page_view(action_title)
        self.assertNotRegexpMatches(
            r,
            'token_auth is authenticated',
            'We are authenticated!',
        )
        self.assertNotRegexpMatches(
            r,
            "New Visit \(IP = %s\)" % self.request.META['REMOTE_ADDR'],
            "IP is different from the request IP",
        )
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
        self.assertRegexpMatches(
            r,
            re.escape(action_title),
            "Action title not found, expected %s" % action_title
        )

    def test_auth(self):
        self.pt.set_token_auth('51e3900f5580128bab770997575e2a00')
        r = self.pt.do_track_page_view(
            self.get_title('test title auth test')
        )
        self.assertRegexpMatches(
            r,
            'token_auth is authenticated',
            'We are not authenticated!',
        )

    def test_auth_ip(self):
        self.pt.set_token_auth('51e3900f5580128bab770997575e2a00')
        ip = self.request.META['REMOTE_ADDR']
        title = self.get_title('ip (auth) %s' % ip)

        r = self.pt.do_track_page_view(title)
        self.assertRegexpMatches(
            r,
            "Visit is known \(IP = %s\)" % ip,
            "IP is different from the request IP, expected %s" % ip
        )

    def test_force_ip(self):
        """
        Well... this unit test could fail randomly if the same random IP is
        chosen again...
        """
        ip = self.random_ip()
        self.pt.set_ip(ip)
        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)
        title = self.get_title('test force ip %s ' % ip)
        r = self.pt.do_track_page_view(title)

        self.assertRegexpMatches(
            r,
            "New Visit \(IP = %s\)" % ip,
            "IP is different from the request IP, expected %s" % ip
        )
        self.assertRegexpMatches(
            r,
            "New Visit \(IP = %s\)" % ip,
            "Overriding the IP didn't work",
        )
        #print r
