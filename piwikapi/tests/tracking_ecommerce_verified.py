import urllib
from random import randint

from piwikapi.tracking import PiwikTrackerEcommerce
from tracking_verified import TrackerVerifyBaseTestCase


class TrackerEcommerceBaseTestCase(TrackerVerifyBaseTestCase):
    """
    Base class for the ecommerce tests

    Contains test products.
    """
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


class TrackerEcommerceVerifyTestCase(TrackerEcommerceBaseTestCase):
    def setUp(self):
        super(TrackerEcommerceVerifyTestCase, self).setUp()
        # Set different IP for each test run
        # TODO also randomize referers etc...
        self.pte = PiwikTrackerEcommerce(self.settings.PIWIK_SITE_ID,
                                         self.request)
        self.pte.set_api_url(self.settings.PIWIK_TRACKING_API_URL)
        self.pte.set_ip(self.get_random_ip())
        self.pte.set_token_auth(self.settings.PIWIK_TOKEN_AUTH)
        self.pte.set_custom_variable(
            5,
            'testsegment',
            self.segment,
        )
        self.pte._set_host("ecommerce.example.com")
        self.pte._set_query_string('')

        self.a.set_method('Live.getLastVisitsDetails')
        self.a.set_parameter('lastMinutes', 1)
        self.a.set_segment("customVariableName5==testsegment;"
            "customVariableValue5==%s" % self.segment)

    def test_ecommerce_view(self):
        # View a product
        product = self.products['book']
        script = "/view/%s/" % urllib.quote(product['name'])
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
        self.assertEqual(
            product['name'],
            self.get_cv(4),
            "Product name %s, not %s" % (self.get_cv(4), product['name'])
        )

    #def test_add_ecommerce_item(self):
    #    """
    #    TODO can't test this directly
    #    """
    #    grand_total = 0
    #    for key, product in self.products.iteritems():
    #        # Put product in the cart
    #        quantity = randint(1, product['quantity'])
    #        self.pte.add_ecommerce_item(
    #            product['sku'],
    #            product['name'],
    #            product['category'],
    #            product['price'],
    #            quantity,
    #        )
    #        grand_total += product['price'] * quantity

    #    title = self.get_title('Add ecommerce items')
    #    r = self.pte.do_track_page_view(title)
    #    import json
    #    data = json.loads(self.a.send_request())
    #    self.debug(data)
    #    self.assertEqual(
    #        title,
    #        self.get_av('pageTitle'),
    #        'Title: "%s", not "%s"' % (self.get_av('pageTitle'), title)
    #    )

    def test_track_ecommerce_order(self):
        """
        TODO We could test that each product was added, not only the sums
        """
        grand_total = 0
        quantity_total = 0
        for key, product in self.products.iteritems():
            # Put product in the cart
            quantity = randint(1, product['quantity'])
            self.pte.add_ecommerce_item(
                product['sku'],
                product['name'],
                product['category'],
                product['price'],
                quantity,
            )
            grand_total += product['price'] * quantity
            quantity_total += quantity
        # Order the products
        script = "/cart/checkout/"
        self.pte._set_script(script)
        r = self.pte.do_track_ecommerce_order(
            randint(0, 99999), # TODO random failure
            grand_total,
        )
        grand_total_string = "%.2f" % grand_total
        revenue = self.get_av('revenue')
        self.assertEqual(
            grand_total_string,
            revenue,
            "Grand total %s, not %s" % (revenue, grand_total_string),
        )
        items = self.get_av('items')
        self.assertEqual(
            str(quantity_total),
            items,
            "Quantity %s, not %s" % (items, quantity_total),
        )
