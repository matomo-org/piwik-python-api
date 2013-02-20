import sys
import unittest
from random import randint
try:
    import json
except ImportError:
    import simplejson as json
try:
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib2 import Request, urlopen
    from urllib import urlencode, quote

from piwikapi.tracking import PiwikTrackerEcommerce
from piwikapi.plugins.goals import PiwikGoals

from tracking import TrackerVerifyBaseTestCase


class TrackerEcommerceBaseTestCase(TrackerVerifyBaseTestCase):
    """
    Base class for the ecommerce tests

    Contains test products.
    """
    products = {
        'book': {
            'sku': '1',
            'name': 'Book',
            'category': ('book category', 'books', ),
            'price': 999,
            'quantity': 3,
        },
        'car': {
            'sku': '2',
            'name': 'Car',
            'category': ('car category', 'cars', ),
            'price': 525,
            'quantity': 3,
        },
        'ball': {
            'sku': '3',
            'name': 'Ball',
            'category': ('ball category', 'balls', ),
            'price': 739,
            'quantity': 7,
        },
    }

    def setUp(self):
        """
        Set up a PiwikTrackerEcommerce instance
        """
        super(TrackerEcommerceBaseTestCase, self).setUp()
        # Set different IP for each test run
        # TODO also randomize referers etc...
        self.pte = PiwikTrackerEcommerce(self.settings['PIWIK_SITE_ID'],
                                         self.request)
        self.pte.set_api_url(self.settings['PIWIK_TRACKING_API_URL'])
        self.pte.set_ip(self.get_random_ip())
        self.pte.set_token_auth(self.settings['PIWIK_TOKEN_AUTH'])
        self.pte.set_custom_variable(
            5,
            'testsegment',
            self.segment,
        )
        self.pte._set_host("ecommerce.example.com")
        self.pte._set_query_string('')

    def get_cv(self, number):
        """
        Get a custom variable from the last visit
        """
        try:
            if sys.version_info[0] >= 3:
                data = json.loads(self.a.send_request().decode('utf-8'))[-1]['actionDetails'][0]['customVariables']
            else:
                data = json.loads(self.a.send_request())[-1]['actionDetails'][0]['customVariables']
        except IndexError:
            print("Request apparently not logged!")
            raise
        try:
            return data[str(number)]['customVariableValue%s' % number]
        except KeyError:
            self.debug(data)
            raise


class TrackerEcommerceVerifyTestCase(TrackerEcommerceBaseTestCase):
    def test_ecommerce_view(self):
        # View a product
        product = self.products['book']
        script = "/view/%s/" % quote(product['name'])
        self.pte._set_script(script)
        self.pte.set_ecommerce_view(
            product['sku'],
            product['name'],
            product['category'],
            product['price'],
        )
        title = self.get_title('Product view %s' % product['name'])
        r = self.pte.do_track_page_view(title)
        self.assertEqual(
            title,
            self.get_av('pageTitle'),
            'Title: "%s", not "%s"' % (self.get_av('pageTitle'), title)
        )
        # TODO verify all data was submitted
        self.assertEqual(
            product['name'],
            self.get_cv(4),
            "Product name %s, not %s" % (self.get_cv(4), product['name'])
        )

    def test_add_ecommerce_item_do_track_ecommerce_cart_update(self):
        """
        Test add_ecommerce_item() together with
        do_track_ecommerce_cart_update(). Also make sure that an abandoned
        cart was logged.
        """
        grand_total = 0
        for key, product in self.products.items():
            # Put product in the cart
            self.pte.add_ecommerce_item(
                product['sku'],
                product['name'],
                product['category'],
                product['price'],
                product['quantity'],
            )
            grand_total += product['price'] * product['quantity']

        title = self.get_title('Add ecommerce items')
        r = self.pte.do_track_ecommerce_cart_update(grand_total)
        items = self.get_av('itemDetails')
        matches = 0
        # The items aren't always stored in the same order as the test code
        # submits them. We could fix this by using time.sleep() but looping
        # through the data is faster.
        for product in list(self.products.values()):
            for item in items:
                if item['itemSKU'] == product['sku']:
                    matches += 1
                    self.assertEqual(
                        product['name'],
                        item['itemName'],
                        "Incorrect product name",
                    )
                    self.assertEqual(
                        str(product['quantity']),
                        item['quantity'],
                        "Incorrect product quantity",
                    )
                    self.assertEqual(
                        product['price'],
                        item['price'],
                        "Incorrect product price",
                    )
        self.assertEqual(
            matches,
            len(self.products),
            "Not all products accounted for",
        )
        # Also check abandoned status
        cart_status = self.get_av('type')
        self.assertEqual(
            cart_status,
            'ecommerceAbandonedCart',
            "Unexpected cart status %s" % cart_status,
        )
        visit_status = self.get_v('visitEcommerceStatus')
        self.assertEqual(
            visit_status,
            'abandonedCart',
            "Unexpected visit status %s" % visit_status,
        )

    def test_track_ecommerce_order(self):
        """
        TODO We could test that each product was added, not only the sums
        """
        grand_total = 0
        quantity_total = 0
        for key, product in self.products.items():
            # Put product in the cart
            self.pte.add_ecommerce_item(
                product['sku'],
                product['name'],
                product['category'],
                product['price'],
                product['quantity'],
            )
            grand_total += product['price'] * product['quantity']
            quantity_total += product['quantity']
        # Order the products
        script = "/cart/checkout/"
        self.pte._set_script(script)
        r = self.pte.do_track_ecommerce_order(
            self.get_unique_string(),
            grand_total,
        )
        revenue = self.get_av('revenue')
        self.assertEqual(
            grand_total,
            revenue,
            "Grand total %s, not %d" % (revenue, grand_total),
        )
        items = self.get_av('items')
        self.assertEqual(
            str(quantity_total),
            items,
            "Quantity %s, not %s" % (items, quantity_total),
        )
