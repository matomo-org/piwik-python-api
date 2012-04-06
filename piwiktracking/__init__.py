import datetime
import json
import md5
import random
import urllib
import urllib2
import urlparse


class PiwikTracker:
    """
    The Piwik Tracker class

    TODO it's probably possible to split the e-commerce stuff into a different
    class
    """
    VERSION = 1
    LENGTH_VISITOR_ID = 16

    def __init__(self, id_site, request):
        random.seed()
        self.request = request
        self.id_site = id_site
        self.api_url = ''
        self.request_cookie = ''
        self.ip = False
        self.token_auth = False
        self.set_request_parameters()
        self.set_local_time(self.get_timestamp())
        self.page_url = self.get_current_url()
        self.cookie_support = True
        self.has_cookies = False
        self.width = False
        self.height = False
        self.visitor_id = self.get_random_visitor_id()
        self.forced_visitor_id = False
        self.debug_append_url = False
        self.page_custom_var = []
        self.ecommerce_items = {}
        self.ecommerce = {}

    def set_request_parameters(self):
        self.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        self.referer = self.request.META.get('HTTP_REFERER', '')
        self.ip = self.request.META.get('REMOTE_ADDR')
        self.accept_language = self.request.META.get('HTTP_ACCEPT_LANGUAGE',
                                                     '')
    def set_local_time(self, datetime):
        "unused"
        self.local_hour = datetime.hour
        self.local_minute = datetime.minute
        self.local_second = datetime.second

    def set_token_auth(self, token_auth):
        """
        Set the auth token for the request. The token can be viewed in the
        user management section of your Piwik install.
        """
        self.token_auth = token_auth

    def set_api_url(self, api_url):
        """
        Set which Piwik API URL to use.
        """
        self.api_url = api_url

    def set_ip(self, ip):
        """
        Set the IP to be tracked. You probably want to use this as the
        request comes from your own server.
        Requires setting the auth token.
        """
        self.ip = ip

    def _set_request_cookie(self, cookie):
        """
        Set the request cookie, for testing purposes
        """
        self.request_cookie = cookie

    def set_browser_has_cookies(self):
        """
        Call this is the browser supports cookies
        """
        self.has_cookies = True

    def set_browser_language(self, language):
        """
        Set the browser language. Piwik uses this to guess the visitor's
        origin when GeoIP is not enabled
        """
        self.accept_language = language

    def set_user_agent(self, user_agent):
        """
        Set the user agent. By default the original request's UA is used.
        """
        self.user_agent = user_agent

    def set_resolution(self, width, height):
        """
        Set the visitor's screen width and height
        """
        self.width = width
        self.height = height

    def set_visitor_id(self, visitor_id):
        if len(visitor_id) != self.LENGTH_VISITOR_ID:
            raise Exception("set_visitor_id() expects a %s character ID" %
                            self.LENGTH_VISITOR_ID)
        self.forced_visitor_id = visitor_id

    def set_debug_string_append(self, string):
        self.debug_append_url = string

    def set_ecommerce_view(self, sku=False, name=False, category=False,
                           price=False):
        """
        Set the page view as an item/product page view, or an ecommerce
        category page view.

        This method will set three custom variables of 'page' scope with the
        SKU, name and category for this page view.

        On a category page you may set the category argument only.

        Tracking product/category page views will allow Piwik to report on
        product and category conversion rates.

        To enable ecommerce tracking see doc/install.rst

        Args:
            SKU (str): Product SKU being viewed
            name (str): Name of the product
            category (str|list): Name of the category for the current category
                page or the product
            price (float): Price of the product
        """
        if category:
            if type(category) == type(list()):
                category = json.dumps(category)
        else:
            category = ''
        self.page_custom_var.append(('_pkc', category))
        if price:
            self.page_custom_var.append(('_pkp', price))
        # On a category page do not record "Product name not defined"
        if sku and name:
            if sku:
                self.page_custom_var.append(('_pks', sku))
            if name:
                self.page_custom_var.append(('_pkn', name))

    def add_ecommerce_item(self, sku, name=False, category=False, price=False,
                           quantity=1):
        """
        Add an item to the ecommerce order.

        This should be called before do_track_ecommerce_order() or before
        do_track_ecommerce_cart_update().

        Thie method can be called for all individual products in the cart/order.

        Args:
            sku (str): Product SKU, mandatory
            name (str): Name of the product
            category (str|list): Name of the category for the current category
                page or the product
            price (float): Price of the product
            quantity (int): Product quantity, defaults to 1
        """
        self.ecommerce_items[sku] = (
            sku,
            name,
            category,
            price,
            quantity
        )

    def do_track_ecommerce_order(self, order_id, grand_total, sub_total=False,
                                  tax=False, shipping=False, discount=False):
        """
        Track an ecommerce order

        If the order contains items you must call add_ecommerce_item() first for
        each item.

        All revenues will be individually summed and reported by Piwik.

        Args:
            order_id (str): Unique order ID (required). Used to avoid
                re-recording an order on page reload.
            grand_total (float): Grand total revenue of the transaction,
                including taxes, shipping, etc.
            sub_total (float): Sub total amount, typicalle the sum of item
                prices for all items in this order, before tax and shipping
            tax (float): Tax amount for this order
            shipping (float): Shipping amount for this order
            discount (float): Discount for this order
        """
        url = self.get_url_track_ecommerce_order(order_id, grand_total,
                                                 sub_total, tax, shipping,
                                                 discount)
        return self._send_request(url)

    def get_current_scheme(self):
        # django-specific
        if self.request.is_secure():
            scheme = 'https'
        else:
            scheme = 'http'
        return scheme

    def get_current_host(self):
        return self.request.META.get('SERVER_NAME', '')

    def get_current_script_name(self):
        return self.request.META.get('PATH_INFO', '')

    def get_current_query_string(self):
        return self.request.META.get('QUERY_STRING', '')

    def get_current_url(self):
        """
        Returns the URL of the page the visitor is on.
        """
        url = self.get_current_scheme() + '://'
        url += self.get_current_host()
        url += self.get_current_script_name()
        url += '?'
        url += self.get_current_query_string()
        return url

    def get_timestamp(self):
        return datetime.datetime.now()

    def get_request(self, id_site):
        """
        This oddly named method returns the query var string.
        """
        query_vars = {
            'idsite': id_site,
            'rec': 1,
            'apiv': self.VERSION,
            'r': random.randint(0, 99999),
            'url': self.page_url,
            'urlref': self.referer,
            'id': self.visitor_id,
        }
        if self.ip:
            query_vars['cip'] = self.ip
        if self.token_auth:
            query_vars['token_auth'] = self.token_auth
        if self.has_cookies:
            query_vars['cookie'] = 1
        if self.width and self.height:
            query_vars['res'] = '%dx%d' % (self.width, self.height)
        if self.forced_visitor_id:
            query_vars['cid'] = self.forced_visitor_id
        url = urllib.urlencode(query_vars)
        if self.debug_append_url:
            url += self.debug_append_url
        return url

    def get_url_track_page_view(self, document_title=False):
        """
        Returns the URL to piwik.php with all parameters set to track the
        pageview

        Args:
            document_title (str): The title of the page the user is on
        """
        url = self.get_request(self.id_site)
        if document_title:
            url += '&%s' % urllib.urlencode({'action_name': document_title})
        return url

    def get_url_track_ecommerce_order(self, order_id, grand_total,
                                      sub_total=False, tax=False,
                                      shipping=False, discount=False):
        """
        Returns an URL used to track ecommerce orders

        Calling this method will reinitialize the property ecommerce_items to
        an empty list. So items will have to be added again via
        add_ecommerce_item()
        """
        url = self.get_url_track_ecommerce(grand_total, sub_total, tax,
                                           shipping, discount)
        url += '&%s' % urllib.urlencode({'ec_id': order_id})
        print '--->', url
        self.ecommerce_last_order_timestamp = self.get_timestamp()
        return url

    def get_url_track_ecommerce(self, grand_total, sub_total=False, tax=False,
                                shipping=False, discount=False):
        """
        Returns the URL used to track ecommerce orders

        Calling this method reinitializes the property ecommerce_items, so
        items will have to be added again via add_ecommerce_item()

        Args:
            Same as...
        """
        if type(grand_total) != type(float()):
            raise Exception("You must specify a grant_total for the ecommerce "
                            "transaction")
        url = self.get_request(self.id_site)
        args = {
            'idgoal': 0,
        }
        if grand_total:
            args['revenue'] = grand_total
        if sub_total:
            args['ec_st'] = sub_total
        if tax:
            args['ec_tx'] = tax
        if shipping:
            args['ec_sh'] = shipping
        if discount:
            args['ec_dt'] = discount
        if len(self.ecommerce_items):
            # Remove the SKU index in the list before JSON encoding
            items = self.ecommerce.values()
            args['ec_items'] = json.dumps(items)
        self.ecommerce_items.clear()
        url += '&%s' % urllib.urlencode(args)
        print '2-->', url
        return url

    def get_visitor_id(self):
        """
        If the user initiating the request has the Piwik first party cookie,
        this function will try and return the ID parsed from this first party
        cookie.

        If you call this function from a server, where the call is triggered by a
        cron or script not initiated by the actual visitor being tracked, then it
        will return the random Visitor ID that was assigned to this visit object.

        This can be used if you wish to record more visits, actions or goals for
        this visitor ID later on.
        """
        if self.forced_visitor_id:
            visitor_id = self.forced_visitor_id
        else:
            id_cookie_name =  'id.%s.' % self.id_site
            id_cookie = self.get_cookie_matching_name(id_cookie_name)
            visitor_id = self.visitor_id
            if id_cookie:
                print 'id_cookie is', id_cookie
                visitor_id = id_cookie
                """
                $visitorId = substr($idCookie, 0, strpos($idCookie, '.'));
                if(strlen($visitorId) == self::LENGTH_VISITOR_ID)
                {
                    return $visitorId;
                """
        return visitor_id

    def get_random_visitor_id(self):
        """
        Return a random visitor ID
        """
        visitor_id = md5.new(str(random.getrandbits(9999))).hexdigest()
        return visitor_id[:self.LENGTH_VISITOR_ID]

    def get_cookie_matching_name(self, name):
        cookie_value = False
        if self.request.COOKIES:
            for name in self.request.COOKIES:
                print 'cookie name', name
                cookie_value = self.request.COOKIES[name]
                print 'cookie is', cookie_value
        #print self.request.COOKIES
        return cookie_value

    def disable_cookie_support(self):
        """
        By default, PiwikTracker will read third party cookies from the
        response and sets them in the next request.
        """
        self.cookie_support = False

    def do_track_page_view(self, document_title):
        """
        Track a page view

        Args:
            document_title (str): The title of the page the user is on
        """
        url = self.get_url_track_page_view(document_title)
        return self._send_request(url)

    def _send_request(self, url):
        """
        Make the tracking API request

        Args:
            url (str): TODO
        """
        parsed = urlparse.urlparse(self.api_url)
        url = "%s://%s%s?%s" % (parsed.scheme, parsed.netloc, parsed.path, url)
        request = urllib2.Request(url)
        request.add_header('User-Agent', self.user_agent)
        request.add_header('Accept-Language', self.accept_language)
        if not self.cookie_support:
            self.request_cookie = ''
        elif self.request_cookie != '':
            print 'Adding cookie', self.request_cookie
            request.add_header('Cookie', self.request_cookie)

        response = urllib2.urlopen(request)
        #print response.info()
        body = response.read()
        # The cookie in the response will be set in the next request
        #for header, value in response.getheaders():
        #    # TODO handle cookies
        #    # set cookie to la
		#	# in case several cookies returned, we keep only the latest one
        #    # (ie. XDEBUG puts its cookie first in the list)
        #    #print header, value
        #    self.request_cookie = ''
        return body


def piwik_get_url_track_page_view(id_site, request, document_title=False):
    tracker = PiwikTracker(id_site, request)
    return tracker.do_track_page_view(document_title)
