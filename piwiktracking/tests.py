import cgi
import unittest
import urllib
import re
from datetime import datetime
from random import randint

from piwiktracking import PiwikTracker
from piwiktracking import PiwikTrackerEcommerce


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


class PiwikTrackerTestBase(unittest.TestCase):
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
        # Standard tracker
        self.pt = PiwikTracker(settings.PIWIK_SITE_ID, self.request)
        self.pt.set_api_url(settings.PIWIK_API_URL)
        # Ecommerce tracker
        self.pte = PiwikTrackerEcommerce(settings.PIWIK_SITE_ID,
                                         self.request)
        self.pte.set_api_url(settings.PIWIK_API_URL)

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

class TestPiwikTrackerAPI(PiwikTrackerTestBase):
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

class TestPiwikTrackerAPINoAutomatedVerification(PiwikTrackerTestBase):
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

    def test_custom_variables(self):
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

        self.pt.set_custom_variable(1, 'foo', value, 'page')
        saved = self.pt.get_custom_variable(1, 'page')
        self.assertEqual(
            value,
            saved[1],
            "Custom page variable was not saved, got %s" % saved[1],
        )

        #c = Client()
        url = self.pt.get_request(settings.PIWIK_SITE_ID)
        #print url
        value = 'quoo'
        self.pt.set_custom_variable(1, 'foo', value, 'visit')
        saved = self.pt.get_custom_variable(1, 'visit')
        self.assertEqual(
            value,
            saved[1],
            "Custom visit variable was not saved, got %s" % saved[1],
        )

        action_title = self.get_title('test custom var')
        r = self.pt.do_track_page_view(action_title)

        #print r


class TestEcommerceStuff(PiwikTrackerTestBase):
    products = {
        'book': {
            'sku': '1',
            'name': 'Book',
            'category': ('test category', 'books', ),
            'price': 9.99,
            'quantity': 5,
        },
        'car': {
            'sku': '2',
            'name': 'Car',
            'category': ('test category', 'cars', ),
            'price': 5.25,
            'quantity': 3,
        },
        'ball': {
            'sku': '3',
            'name': 'Ball',
            'category': ('test category', 'balls', ),
            'price': 7.39,
            'quantity': 10,
        },
    }

    def browse_and_put_into_cart(self):
        # Set different IP for each test run
        # TODO also randomize referers etc...
        self.pte.set_ip(self.random_ip())
        self.pte.set_token_auth(settings.PIWIK_TOKEN_AUTH)

        grand_total = 0
        for key, product in self.products.iteritems():
            if randint(0, 2) == 0:
                continue

            # View the category page
            category = product['category'][1]
            self.pte._set_script("/category/%s/" % urllib.quote(category))
            r = self.pte.do_track_page_view(self.get_title('Category %s' %
                                            category))

            # View the product
            self.pte._set_host("ecommerce.example.com")
            self.pte._set_query_string('')
            self.pte._set_script("/view/%s/" % urllib.quote(product['name']))
            self.pte.set_ecommerce_view(
                product['sku'],
                product['name'],
                product['category'],
                product['price'],
            )
            r = self.pte.do_track_page_view(self.get_title('view %s'
                                            % product['name']))

            # Put it in the cart
            quantity = randint(1, product['quantity'])
            self.pte.add_ecommerce_item(
                product['sku'],
                product['name'],
                product['category'],
                product['price'],
                quantity,
            )
            grand_total += product['price'] * quantity

        # Update the cart
        self.pte._set_script("/cart/checkout/")
        #r = self.pte.do_track_ecommerce_cart_update(grand_total)
        # Order the products
        r = self.pte.do_track_ecommerce_order(
            randint(0, 99999), # TODO random failure
            grand_total,
        )
        #print r
        return grand_total

    def test_set_ecommerce_view(self):
        grand_total = self.browse_and_put_into_cart()
        grand_total = self.browse_and_put_into_cart()
        grand_total = self.browse_and_put_into_cart()


if __name__ == '__main__':
    unittest.main()
