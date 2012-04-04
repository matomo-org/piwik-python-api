import datetime
import httplib
import random
import urllib
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

    def set_request_parameters(self):
        # django-specific
        self.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        self.referer = self.request.META.get('HTTP_REFERER', '')
        self.ip = self.request.META.get('REMOTE_ADDR')
        self.accept_language = self.request.META.get(
            'HTTP_ACCEPT_LANGUAGE', '')

    def set_local_time(self, datetime):
        self.local_hour = datetime.hour
        self.local_minute = datetime.minute
        self.local_second = datetime.second

    def set_token_auth(self, token_auth):
        self.token_auth = token_auth

    def set_api_url(self, api_url):
        self.api_url = api_url

    def set_ip(self, ip):
        self.ip = ip

    def get_current_scheme(self):
        # django-specific
        if self.request.is_secure():
            scheme = 'https'
        else:
            scheme = 'http'
        return scheme

    def get_current_host(self):
        # django-specific
        return self.request.get_host()

    def get_current_script_name(self):
        # django-specific
        return self.request.path_info

    def get_current_query_string(self):
        # django-specific
        return self.request.META.get('QUERY_STRING', '')

    def get_current_url(self):
        url = self.get_current_scheme() + '://'
        url += self.get_current_host()
        url += self.get_current_script_name()
        url += '?'
        url += self.get_current_query_string()
        return url

    def get_timestamp(self):
        return datetime.datetime.now()

    def get_request(self, id_site, document_title):
        query_vars = {
            'idsite': id_site,
            'rec': 1,
            'apiv': self.VERSION,
            'r': random.randint(0, 99999),
            'url': self.page_url,
            'urlref': self.referer,
        }
        if self.ip:
            query_vars['cip'] = self.ip
        if self.token_auth:
            query_vars['token_auth'] = self.token_auth
        if document_title:
            query_vars['action_name'] = document_title
        return urllib.urlencode(query_vars)

    def get_visitor_id(self):
        pass

    def get_url_track_page_view(self, document_title=False):
        url = self.get_request(self.id_site, document_title)
        return url

    #def get_visitor_id(self):
    #    id_cookie_name =  'id.%s.' % self.id_site
    #    id_cookie = self.get_cookie_matching_name(id_cookie_name)
    #    visitor_id = self.visitor_id
    #    if id_cookie:
    #        print 'id_cookie is', id_cookie
    #        visitor_id = id_cookie
    #        """
    #		$visitorId = substr($idCookie, 0, strpos($idCookie, '.'));
    #		if(strlen($visitorId) == self::LENGTH_VISITOR_ID)
    #		{
    #			return $visitorId;
    #        """
    #    return visitor_id

    def get_cookie_matching_name(self, name):
        cookie_value = False
        print self.request.COOKIES
        if name in self.request.COOKIES:
            cookie_value = self.request.COOKIES[name]
            print 'cookie is', cookie_value
        return cookie_value

    def do_track_page_view(self, document_title):
        url = self.get_url_track_page_view(document_title)
        return self.send_request(url)

    def send_request(self, url):
        "Send the request to piwik"
        headers = {
            'Accept-Language': self.accept_language,
            'User-Agent': self.user_agent,
            'Cookie': self.request_cookie,
        }
        parsed = urlparse.urlparse(self.api_url)
        url = "%s?%s" % (parsed.path, url)

        connection = httplib.HTTPConnection(parsed.hostname)
        connection.request('GET', url, '', headers)
        response = connection.getresponse()
        return response.read()


def piwik_get_url_track_page_view(id_site, document_title=False, request):
    tracker = PiwikTracker(id_site, request)
    return tracker.do_track_page_view(document_title)
