"""
Copyright (c) 2012, Nicolas Kuttler.
All rights reserved.

License: BSD, see LICENSE for details

Source and development at https://github.com/nkuttler/python-piwikapi
"""

import datetime
import json
import logging
import md5
import os
import random
import urllib
import urllib2
import urlparse

from exceptions import ConfigurationError
from exceptions import InvalidParameter


class PiwikTracker(object):
    """
    The Piwik tracker class
    """
    # Piwik API version
    VERSION = 1

    #: Length of the visitor ID
    LENGTH_VISITOR_ID = 16

    #: List of plugins Piwik knows
    KNOWN_PLUGINS = {
        'flash': 'fla',
        'java': 'java',
        'director': 'dir',
        'quick_time': 'qt',
        'real_player': 'realp',
        'pdf': 'pdf',
        'windows_media': 'wma',
        'gears': 'gears',
        'silverlight': 'ag',
    }

    UNSUPPORTED_WARNING = "%s: The code that's just running is untested and " \
        "probably doesn't work as expected anyway."

    def __init__(self, id_site, request):
        """
        :param id_site: Site ID
        :type id_site: int
        :param request: Request
        :type request: A Django-like request object
        :rtype: None
        """
        random.seed()
        self.request = request
        self.host = self.request.META.get('SERVER_NAME', '')
        self.script = self.request.META.get('PATH_INFO', '')
        self.query_string = self.request.META.get('QUERY_STRING', '')
        self.id_site = id_site
        self.api_url = ''
        self.request_cookie = ''
        self.ip = False
        self.token_auth = False
        self.__set_request_parameters()
        self.forced_datetime = False
        self.set_local_time(self._get_timestamp())
        self.page_url = self.__get_current_url()
        self.cookie_support = True
        self.has_cookies = False
        self.width = False
        self.height = False
        self.visitor_id = self.get_random_visitor_id()
        self.forced_visitor_id = False
        self.debug_append_url = False
        self.page_custom_var = {}
        self.visitor_custom_var = {}
        self.plugins = {}
        self.attribution_info = {}

    def __set_request_parameters(self):
        """
        Set some headers for the request

        :rtype: None
        """
        self.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        self.referer = self.request.META.get('HTTP_REFERER', '')
        #self.ip = self.request.META.get('REMOTE_ADDR')
        self.accept_language = self.request.META.get('HTTP_ACCEPT_LANGUAGE',
                                                     '')

    def set_local_time(self, datetime):
        """
        Set the time

        :param datetime: Time
        :type datetime: datetime.datetime object
        :rtype: None
        """
        self.local_hour = datetime.hour
        self.local_minute = datetime.minute
        self.local_second = datetime.second

    def set_token_auth(self, token_auth):
        """
        Set the auth token for the request. The token can be viewed in the
        user management section of your Piwik install.

        :param token_auth: Auth token
        :type token_auth: str
        :rtype: None
        """
        self.token_auth = token_auth

    def set_api_url(self, api_url):
        """
        Set which Piwik API URL to use

        :param api_url: API URL
        :type api_url: str
        :rtype: None
        """
        self.api_url = api_url

    def set_ip(self, ip):
        """
        Set the IP to be tracked. You probably want to use this as the
        request comes from your own server.

        Requires setting the auth token.

        :param ip: IP
        :type ip: str
        :rtype: None
        """
        self.ip = ip

    def set_browser_has_cookies(self):
        """
        Call this is the browser supports cookies

        :rtype: None
        """
        self.has_cookies = True

    def set_browser_language(self, language):
        """
        Set the browser language. Piwik uses this to guess the visitor's
        origin when GeoIP is not enabled

        :param language: Accept-Language
        :type language: str
        :rtype: None
        """
        self.accept_language = language

    def set_user_agent(self, user_agent):
        """
        Set the user agent. By default the original request's UA is used.

        :param user_agent: User agent
        :type user_agent: str
        :rtype: None
        """
        self.user_agent = user_agent

    def set_resolution(self, width, height):
        """
        Set the visitor's screen width and height

        :param width: Screen width
        :type width: int or str
        :param height: Screen height
        :type height: int or str
        :rtype: None
        """
        self.width = width
        self.height = height

    def set_visitor_id(self, visitor_id):
        """
        :param visitor_id: Visitor I
        :type visitor_id: str
        :raises: InvalidParameter if the visitor_id has an incorrect length
        :rtype: None
        """
        if len(visitor_id) != self.LENGTH_VISITOR_ID:
            raise InvalidParameter("set_visitor_id() expects a visitor ID of "
                                   "length %s" % self.LENGTH_VISITOR_ID)
        self.forced_visitor_id = visitor_id

    def set_debug_string_append(self, string):
        """
        :param string: str to append
        :type string: str
        :rtype: None
        """
        self.debug_append_url = string

    def set_url_referer(self, referer):
        """
        Set the referer URL

        :param referer: Referer
        :type referer: str
        :rtype: None
        """
        self.referer = referer

    def set_url(self, url):
        """
        Set URL being tracked

        :param url: URL
        :type url: str
        """
        self.page_url = url

    def set_attribution_info(self, json_encoded):
        """
        **NOT SUPPORTED**

        Set the attribution info for the visit, so that subsequent goal
        conversions are properly attributed to the right referer, timestamp,
        campaign name and keyword.

        This must be a JSON encoded string that you would normally fetch from
        the Javascript API, see function getAttributionInfo() in
        http://dev.piwik.org/trac/browser/trunk/js/piwik.js

        :param json_encoded: JSON encoded list containing attribution info
        :type json_encoded: string
        :raises: InvalidParameter if the json_encoded data is incorrect
        :rtype: none
        """
        logging.warn(self.UNSUPPORTED_WARNING % 'set_attribution_info()')
        decoded = json.loads(json_encoded)
        if type(decoded) != type(list()):
            raise InvalidParameter("set_attribution_info() is expecting a "
                                   "JSON encoded string, %s given" %
                                   json_encoded)
        if len(decoded) != 4:
            raise InvalidParameter("set_attribution_info() is expecting a "
                                   "JSON encoded string, that contains a list "
                                   "with four items, %s given" % json_encoded)
        self.attribution_info = decoded

    def set_force_visit_date_time(self, datetime):
        """
        Override the server date and time for the tracking request.

        By default Piwik tracks requests for the "current" datetime, but
        this method allows you to track visits in the past. Time are in
        UTC.

        Requires setting the auth token.

        :param datetime: datetime
        :type datetime: datetime.datetime object
        :rtype: None
        """
        self.forced_datetime = datetime

    def __set_request_cookie(self, cookie):
        """
        Set the request cookie, for testing purposes

        :param cookie: Request cookie
        :type cookie: str
        :rtype: None
        """
        self.request_cookie = cookie

    def _set_host(self, host):
        """
        Used for unit tests

        :param host: Hostname
        :type host: str
        :rtype: None
        """
        self.host = host
        self.page_url = self.__get_current_url()

    def _set_query_string(self, query_string):
        """
        Used for unit tests

        :param query_string: Query string
        :type query_string: str
        :rtype: None
        """
        self.query_string = query_string
        self.page_url = self.__get_current_url()

    def _set_script(self, script):
        """
        Used for unit tests

        :param script: Script name
        :type script: str
        :rtype: None
        """
        self.script = script
        self.page_url = self.__get_current_url()

    def __get_current_scheme(self):
        """
        Return either http or https

        :rtype: str
        """
        # django-specific
        if self.request.is_secure():
            scheme = 'https'
        else:
            scheme = 'http'
        return scheme

    def __get_current_host(self):
        """
        :rtype: str
        """
        return self.host

    def __get_current_script_name(self):
        """
        :rtype: str
        """
        return self.script

    def __get_current_query_string(self):
        """
        :rtype: str
        """
        return self.query_string

    def __get_current_url(self):
        """
        Returns the URL of the page the visitor is on.

        :rtype: str
        """
        url = self.__get_current_scheme() + '://'
        url += self.__get_current_host()
        url += self.__get_current_script_name()
        if self.__get_current_query_string():
            url += '?'
            url += self.__get_current_query_string()
        return url

    def _get_timestamp(self):
        """
        Returns the timestamp for the request

        Defaults to current datetime but can be set through
        set_force_visit_date_time().

        :rtype: datetime.datetime object
        """
        if self.forced_datetime:
            r = self.forced_datetime
        else:
            r = datetime.datetime.now()
        return r

    def _get_request(self, id_site):
        """
        This oddly named method returns the query var string.

        :param id_site: Site ID
        :type id_site: int
        :rtype: str
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
        if self.page_custom_var:
            query_vars['cvar'] = json.dumps(self.page_custom_var)
        if self.visitor_custom_var:
            query_vars['_cvar'] = json.dumps(self.visitor_custom_var)
        if len(self.plugins):
            for plugin, version in self.plugins.iteritems():
                query_vars[plugin] = version
        if len(self.attribution_info):
            for i, var in {
                0: '_rcn',
                1: '_rck',
                2: '_refts',
                3: '_ref',
            }.iteritems():
                query_vars[var] = urllib.quote(self.attribution_info[i])

        url = urllib.urlencode(query_vars)
        if self.debug_append_url:
            url += self.debug_append_url
        return url

    def __get_url_track_page_view(self, document_title=''):
        """
        Returns the URL to piwik.php with all parameters set to track the
        pageview

        :param document_title: The title of the page the user is on
        :type document_title: str
        :rtype: str
        """
        url = self._get_request(self.id_site)
        if document_title:
            url += '&%s' % urllib.urlencode({'action_name': document_title})
        return url

    def __get_url_track_action(self, action_url, action_type):
        """
        :param action_url: URL of the download or outlink
        :type action_url: str
        :param action_type: Type of the action, either 'download' or 'link'
        :type action_type: str
        """
        url = self._get_request(self.id_site)
        url += "&%s" % urllib.urlencode({action_type: action_url})
        return url

    def __get_cookie_matching_name(self, name):
        """
        **NOT SUPPORTED**

        Get a cookie's value by name

        :param name: Cookie name
        :type name: str
        :rtype: str
        """
        logging.warn(self.UNSUPPORTED_WARNING % '__get_cookie_matching_name()')
        cookie_value = False
        if self.request.COOKIES:
            for name in self.request.COOKIES:
                #print 'cookie name', name
                #print 'cookie is', cookie_value
                cookie_value = self.request.COOKIES[name]
        #print self.request.COOKIES
        return cookie_value

    def get_visitor_id(self):
        """
        **PARTIAL, no cookie support**

        If the user initiating the request has the Piwik first party cookie,
        this function will try and return the ID parsed from this first party
        cookie.

        If you call this function from a server, where the call is triggered by
        a cron or script not initiated by the actual visitor being tracked,
        then it will return the random Visitor ID that was assigned to this
        visit object.

        This can be used if you wish to record more visits, actions or goals
        for this visitor ID later on.

        :rtype: str
        """
        if self.forced_visitor_id:
            visitor_id = self.forced_visitor_id
        else:
            logging.warn(self.UNSUPPORTED_WARNING % 'get_visitor_id()')
            id_cookie_name = 'id.%s.' % self.id_site
            id_cookie = self.__get_cookie_matching_name(id_cookie_name)
            visitor_id = self.visitor_id
            if id_cookie:
                #print 'id_cookie is', id_cookie
                visitor_id = id_cookie
                #$visitorId = substr($idCookie, 0, strpos($idCookie, '.'));
                #if(strlen($visitorId) == self::LENGTH_VISITOR_ID)
                #{
                #    return $visitorId;
        return visitor_id

    def get_attribution_info(self):
        """
        **NOT SUPPORTED**

        To support this we'd need to parse the cookies in the request obejct.
        Not sure if this makes sense...

        Return the currently assigned attribution info stored in a first party
        cookie.

        This method only works if the user is initiating the current request
        and his cookies can be read by this API.

        :rtype: string, JSON encoded string containing the referer info for
            goal conversion attribution
        """
        logging.warn(self.UNSUPPORTED_WARNING % 'get_attribution_info()')
        attribution_cookie_name = 'ref.%d.' % self.id_site
        return self.__get_cookie_matching_name(attribution_cookie_name)

    def __get_random_string(self, length=500):
        """
        Return a random string

        :param length: Length
        :type length: inte
        :rtype: str
        """
        return md5.new(os.urandom(length)).hexdigest()

    def get_random_visitor_id(self):
        """
        Return a random visitor ID

        :rtype: str
        """
        visitor_id = self.__get_random_string()
        return visitor_id[:self.LENGTH_VISITOR_ID]

    def disable_cookie_support(self):
        """
        **NOT TESTED**

        By default, PiwikTracker will read third party cookies from the
        response and sets them in the next request.

        :rtype: None
        """
        logging.warn(self.UNSUPPORTED_WARNING % 'disable_cookie_support()')
        self.cookie_support = False

    def do_track_page_view(self, document_title):
        """
        Track a page view, return the request body

        :param document_title: The title of the page the user is on
        :type document_title: str
        :rtype: str
        """
        url = self.__get_url_track_page_view(document_title)
        return self._send_request(url)

    def do_track_action(self, action_url, action_type):
        """
        Track a download or outlink

        :param action_url: URL of the download or outlink
        :type action_url: str
        :param action_type: Type of the action, either 'download' or 'link'
        :type action_type: str
        :raises: InvalidParameter if action type is unknown
        :rtype: str
        """
        if action_type not in ('download', 'link'):
            raise InvalidParameter("Illegal action parameter %s" % action_type)
        url = self.__get_url_track_action(action_url, action_type)
        return self._send_request(url)

    def _send_request(self, url):
        """
        Make the tracking API request, return the request body

        :param url: TODO
        :type url: str
        :raises: ConfigurationError if the API URL was not set
        :rtype: str
        """
        if self.api_url == '':
            raise ConfigurationError('API URL not set')
        parsed = urlparse.urlparse(self.api_url)
        url = "%s://%s%s?%s" % (parsed.scheme, parsed.netloc, parsed.path, url)
        request = urllib2.Request(url)
        request.add_header('User-Agent', self.user_agent)
        request.add_header('Accept-Language', self.accept_language)
        if not self.cookie_support:
            self.request_cookie = ''
        elif self.request_cookie != '':
            #print 'Adding cookie', self.request_cookie
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

    def set_custom_variable(self, id, name, value, scope='visit'):
        """
        Set a custom variable

        See http://piwik.org/docs/custom-variables/

        :param id: Custom variable slot ID, 1-5
        :type id: int
        :param name: Variable name
        :type name: str
        :param value: Variable value
        :type value: str
        :param scope: Variable scope, either visit or page,
            defaults to visit
        :type scope: str or None
        :rtype: None
        """
        if type(id) != type(int()):
            raise InvalidParameter("Parameter id must be int, not %s" %
                                   type(id))
        if scope == 'page':
            self.page_custom_var[id] = (name, value)
        elif scope == 'visit':
            self.visitor_custom_var[id] = (name, value)
        else:
            raise InvalidParameter("Invalid scope parameter value %s" % scope)

    def set_plugins(self, **kwargs):
        """
        Set supported plugins

        >>> piwiktrackerinstance.set_plugins(flash=True)

        See KNOWN_PLUGINS keys for valid values.

        :param kwargs: A plugin: version dict, e.g. {'java': 6}, see also
            KNOWN_PLUGINS
        :type kwargs: dict of {str: int}
        :rtype: None
        """
        for plugin, version in kwargs.iteritems():
            if plugin not in self.KNOWN_PLUGINS.keys():
                raise ConfigurationError("Unknown plugin %s, please use one "
                                         "of %s" % (plugin,
                                                    self.KNOWN_PLUGINS.keys()))
            self.plugins[self.KNOWN_PLUGINS[plugin]] = int(version)

    def get_custom_variable(self, id, scope='visit'):
        """
        **PARTIAL, no cookie support**

        Returns the current custom variable stored in a first party cookie.

        :param id: Custom variable slot ID, 1-5
        :type id: int
        :param scope: Variable scope, either visit or page
        :type scope: str
        :rtype: mixed stuff TODO
        """
        if type(id) != type(int()):
            raise InvalidParameter("Parameter id must be int, not %s" %
                                   type(id))
        if scope == 'page':
            r = self.page_custom_var[id]
        elif scope == 'visit':
            if self.visitor_custom_var[id]:
                r = self.visitor_custom_var[id]
            else:
                logging.warn(self.UNSUPPORTED_WARNING %
                             'get_custom_variable()')
                # TODO test this code...
                custom_vars_cookie = 'cvar.%d.' % self.id_site
                cookie = self.__get_cookie_matching_name(custom_vars_cookie)
                if not cookie:
                    r = False
                else:
                    cookie_decoded = json.loads(cookie)
                    #$cookieDecoded = json_decode($cookie, $assoc = true);
                    #print 'decoded cookie json', cookie_decode
                    #print 'decoded cookie json', repr(cookie_decode)
                    if type(cookie_decoded) == type(list()):
                        r = False
                    elif id not in cookie_decoded:
                        r = False
                    elif len(cookie_decoded[id]) != 2:
                        r = False
                    else:
                        r = cookie_decoded[id]
        else:
            raise InvalidParameter("Invalid scope parameter value %s" % scope)
        return r


class PiwikTrackerEcommerce(PiwikTracker):
    """
    The Piwik tracker class for ecommerce
    """
    def __init__(self, id_site, request):
        self.ecommerce_items = {}
        super(PiwikTrackerEcommerce, self).__init__(id_site, request)

    def __get_url_track_ecommerce_order(self, order_id, grand_total,
                                      sub_total=False, tax=False,
                                      shipping=False, discount=False):
        """
        Returns an URL used to track ecommerce orders

        Calling this method will reinitialize the property ecommerce_items to
        an empty list. So items will have to be added again via
        add_ecommerce_item().

        :param order_id: Unique order ID (required). Used to avoid
            re-recording an order on page reload.
        :type order_id: str
        :param grand_total: Grand total revenue of the transaction,
            including taxes, shipping, etc.
        :type grand_total: float
        :param sub_total: Sub total amount, typicalle the sum of
            item prices for all items in this order, before tax and shipping
        :type sub_total: float or None
        :param tax: Tax amount for this order
        :type tax: float or None
        :param shipping: Shipping amount for this order
        :type shipping: float or None
        :param discount: Discount for this order
        :type discount: float or None
        :rtype: str
        """
        url = self.__get_url_track_ecommerce(grand_total, sub_total, tax,
                                           shipping, discount)
        url += '&%s' % urllib.urlencode({'ec_id': order_id})
        self.ecommerce_last_order_timestamp = self._get_timestamp()
        return url

    def __get_url_track_goal(self, id_goal, revenue=False):
        """
        Return the goal tracking URL

        :param id_goal: Goal ID
        :type id_goal: int
        :param revenue: Revenue for this conversion
        :type revenue: int (TODO why int here and not float!?)
        """
        url = self._get_request(self.id_site)
        params = {}
        params['idgoal'] = id_goal
        if revenue:
            params['revenue'] = revenue
        url += '&%s' % urllib.urlencode(params)
        return url

    def __get_url_track_ecommerce(self, grand_total, sub_total=False,
                                  tax=False, shipping=False, discount=False):
        """
        Returns the URL used to track ecommerce orders

        Calling this method reinitializes the property ecommerce_items, so
        items will have to be added again via add_ecommerce_item()

        :param grand_total: Grand total revenue of the transaction,
            including taxes, shipping, etc.
        :type grand_total: float
        :param sub_total: Sub total amount, typicalle the sum of
            item prices for all items in this order, before tax and shipping
        :type sub_total: float or None
        :param tax: Tax amount for this order
        :type tax: float or None
        :param shipping: Shipping amount for this order
        :type shipping: float or None
        :param discount: Discount for this order
        :type discount: float or None
        :rtype: str
        """
        # FIXME fix what?
        url = self._get_request(self.id_site)
        args = {
            'idgoal': 0,
        }
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
            items = self.ecommerce_items.values()
            args['ec_items'] = json.dumps(items)
        self.ecommerce_items.clear()
        url += '&%s' % urllib.urlencode(args)
        return url

    def __get_url_track_ecommerce_cart_update(self, grand_total):
        """
        Returns the URL to track a cart update

        :type grand_total: float
        :param grand_total: Grand total revenue of the transaction,
            including taxes, shipping, etc.
        :type grand_total: float
        :rtype: str
        """
        url = self.__get_url_track_ecommerce(grand_total)
        return url

    def add_ecommerce_item(self, sku, name=False, category=False, price=False,
                           quantity=1):
        """
        Add an item to the ecommerce order.

        This should be called before do_track_ecommerce_order() or before
        do_track_ecommerce_cart_update().

        This method can be called for all individual products in the
        cart/order.

        :param sku: Product SKU
        :type SKU: str or None
        :param name: Name of the product
        :type name: str or None
        :param category: Name of the category for the current
            category page or the product
        :type category: str, list or None
        :param price: Price of the product
        :type price: float or None
        :param quantity: Product quantity, defaults to 1
        :type price: int or None
        :rtype: None
        """
        self.ecommerce_items[sku] = (
            sku,
            name,
            category,
            price,
            quantity,
        )

    def do_track_ecommerce_cart_update(self, grand_total):
        """
        Track a cart update (add/remove/update item)

        On every cart update you must call add_ecommerce_item() for each item
        in the cart, including items which were in the previous cart. Items
        get deleted until they are re-submitted.

        :type grand_total: float
        :param grand_total: Grand total revenue of the transaction,
            including taxes, shipping, etc.
        :type grand_total: float
        :rtype: str
        """
        # FIXME
        url = self.__get_url_track_ecommerce_cart_update(grand_total)
        return self._send_request(url)

    def do_track_ecommerce_order(self, order_id, grand_total, sub_total=False,
                                  tax=False, shipping=False, discount=False):
        """
        Track an ecommerce order

        If the order contains items you must call add_ecommerce_item() first
        for each item.

        All revenues will be individually summed and reported by Piwik.

        :param order_id: Unique order ID (required). Used to avoid
            re-recording an order on page reload.
        :type order_id: str
        :param grand_total: Grand total revenue of the transaction,
            including taxes, shipping, etc.
        :type grand_total: float
        :param sub_total: Sub total amount, typicalle the sum of
            item prices for all items in this order, before tax and shipping
        :type sub_total: float or None
        :param tax: Tax amount for this order
        :type tax: float or None
        :param shipping: Shipping amount for this order
        :type shipping: float or None
        :param discount: Discount for this order
        :type discount: float or None
        :rtype: str
        """
        url = self.__get_url_track_ecommerce_order(order_id, grand_total,
                                                   sub_total, tax, shipping,
                                                   discount)
        return self._send_request(url)

    def do_track_goal(self, id_goal, revenue=False):
        """
        Record a goal conversion

        :param id_goal: Goal ID
        :type id_goal: int
        :param revenue: Revenue for this conversion
        :type revenue: int (TODO why int here and not float!?)
        :rtype: str
        """
        url = self.__get_url_track_goal(id_goal, revenue)
        return self._send_request(url)

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

        :param SKU: Product SKU being viewed
        :type SKU: str or None
        :param name: Name of the product
        :type name: str or None
        :param category: Name of the category for the current
            category page or the product
        :type category: str, list or None
        :param price: Price of the product
        :type price: float or None
        :rtype: None
        """
        if category:
            if type(category) == type(list()):
                category = json.dumps(category)
        else:
            category = ''
        self.page_custom_var[5] = ('_pkc', category)
        if price:
            self.page_custom_var[2] = ('_pkp', price)
        # On a category page do not record "Product name not defined"
        if sku and name:
            if sku:
                self.page_custom_var[3] = ('_pks', sku)
            if name:
                self.page_custom_var[4] = ('_pkn', name)


def piwik_get_url_track_page_view(id_site, request, document_title=''):
    tracker = PiwikTracker(id_site, request)
    return tracker.do_track_page_view(document_title)
