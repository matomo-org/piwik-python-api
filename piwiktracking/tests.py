import cgi
import unittest
import re
from datetime import datetime
from random import randint

from piwiktracking import PiwikTracker


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

    #: Cookies... work in progress
    COOKIES = False

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
            'REMOTE_ADDR': self.random_ip(),
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

    def test_set_visitor_id(self):
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
        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)
        r = self.pt.do_track_page_view(self.get_title('visitor id with auth'))
        self.assertRegexpMatches(
            r,
            'Matching visitors with: visitorId=%s' % id,
            "Visitor ID not found in response"
        )

        #self.assertTrue(False)

class TestPiwikTrackerAPINoAutomatedVerification(TestPiwikTrackerAPI):
    """
    Here are test we don't verify programmatically yet. I guess we'd have to
    access the Piwik API to fetch data to verify the tracking requests were
    processed properly. At the moment I only check this manually in my Piwik
    dev installation.
    """
    def test_browser_has_cookies(self):
        self.pt.set_browser_has_cookies()
        cookie = "piwiktrackingtest=yes; hascookies=yes"
        self.pt._set_request_cookie(cookie)
        self.assertTrue(True) # FIXME

    def test_set_resolution(self):
        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH) # verify hack
        self.pt.set_resolution(5760, 1080)
        r = self.pt.do_track_page_view(self.get_title('set resolution test'))
        self.assertTrue(True) # FIXME

    def test_set_browser_language(self):
        language = 'de-de'
        self.pt.set_browser_language(language)
        self.assertEqual(
            language,
            self.pt.accept_language,
            "Browser language was not set to %s" % language
        )

    def test_set_user_agent(self):
        ua = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/' \
            'bot.html)'
        self.pt.set_user_agent(ua)
        self.assertEqual(
            ua,
            self.pt.user_agent,
            "User Agent was not set to %s" % ua
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

    def test_set_ecommerce_view(self):
        # Set different IP for each test run
        # TODO also randomize referers etc...
        self.pt.set_ip(self.random_ip())
        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH)
        products = {
            'book': {
                'sku': '1234',
                'name': 'Test book',
                'category': ('test category', 'books', ),
                'price': 9.99,
                'quantity': 21,
            },
            'car': {
                'sku': '1235',
                'name': 'Test car',
                'category': ('test category', 'cars', ),
                'price': 5.25,
                'quantity': 1,
            },
        }
        grand_total = 0
        for key, product in products.iteritems():
            # View all products
            self.pt.set_ecommerce_view(
                product['sku'],
                product['name'],
                product['category'],
                product['price'],
            )
            r = self.pt.do_track_page_view(self.get_title('view %s'
                                           % product['name']))
            # Put them in the cart
            self.pt.add_ecommerce_item(
                product['sku'],
                product['name'],
                product['category'],
                product['price'],
                product['quantity'],
            )
            grand_total += product['price'] * product['quantity']
        # Order them
        r = self.pt.do_track_ecommerce_order(
            randint(0, 99999), # TODO random failure
            grand_total,
        )

        #self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
