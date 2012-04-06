import datetime
import md5
import random
import urllib
import urllib2
import urlparse


class PiwikTracker:
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

    def get_request(self, id_site, document_title):
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
        if document_title:
            query_vars['action_name'] = document_title
        if self.has_cookies:
            query_vars['cookie'] = 1
        if self.width and self.height:
            query_vars['res'] = '%dx%d' % (self.width, self.height)
        if self.forced_visitor_id:
            query_vars['cid'] = self.forced_visitor_id
        return urllib.urlencode(query_vars)

    def get_url_track_page_view(self, document_title=False):
        """
        Returns the URL to piwik.php with all parameters set to track the
        pageview

        Args:
            document_title (str): Page view name as it will appear in Piwik
            reports
        """
        url = self.get_request(self.id_site, document_title)
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
        #print "1 get_visitor_id() returns:", visitor_id
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
       # print self.request.COOKIES
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
            document_title: The title of the page the user is on
        """
        url = self.get_url_track_page_view(document_title)
        return self._send_request(url)

    def _send_request(self, url):
        """
        Make the tracking API request

        Args:
            url -- TODO
        """
        parsed = urlparse.urlparse(self.api_url)
        url = "%s://%s%s?%s" % (parsed.scheme, parsed.netloc, parsed.path, url)
        #url = 'http://piwik.kuttler.eu'
        #print 'XXX', url
        request = urllib2.Request(url)
        request.add_header('User-Agent', self.user_agent)
        #headers = {
        #    'Accept-Language': self.accept_language,
        #    'User-Agent': self.user_agent,
        #    #'Cookie': self.request_cookie,
        #}
        #print headers
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
