import urllib
from random import randint

from base import PiwikAPITestCase
from piwikapi.tracking import PiwikTrackerEcommerce


class TrackerEcommerceBaseTestCase(PiwikAPITestCase):
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

    def setUp(self):
        super(TrackerEcommerceBaseTestCase, self).setUp()
        self.pte = PiwikTrackerEcommerce(self.settings.PIWIK_SITE_ID,
                                         self.request)
        self.pte.set_api_url(self.settings.PIWIK_TRACKING_API_URL)


class TrackerEcommerceNoverifyTestCase(TrackerEcommerceBaseTestCase):
    """
    Ecommerce unit tests
    """
    def test_browse_cart_update_order(self):
        """
        This is a test shopping run. The visitor will browse from category to
        product page and buy a random amount of products. These values should
        probably be hardcoded so that we can verify them.. or maybe we can use
        the analytics API once we have written it..
        """
        # Set different IP for each test run
        # TODO also randomize referers etc...
        self.pte.set_ip(self.get_random_ip())
        self.pte.set_token_auth(self.settings.PIWIK_TOKEN_AUTH)

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

        # Order the products
        #r = self.pte.do_track_ecommerce_cart_update(grand_total)
        self.pte._set_script("/cart/checkout/")
        #print repr(grand_total)
        r = self.pte.do_track_ecommerce_order(
            randint(0, 99999), # TODO random failure
            grand_total,
        )
        #print r
        return grand_total
