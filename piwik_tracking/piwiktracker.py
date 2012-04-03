import datetime
import httplib
import random
import urllib
import urlparse


class PiwikTracker:
    VERSION = 1

    def __init__(self, id_site, api_url, request, token_auth):
        random.seed()
        self.id_site = id_site
        self.api_url = api_url
        self.request = request
        self.token_auth = token_auth

        self.page_url = self.get_current_url()
        self.set_request_parameters()
        self.set_local_time(self.get_timestamp())

    def set_request_parameters(self):
        # django-specific
        self.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        self.referer = self.request.META.get('HTTP_REFERER', '')
        self.ip = self.request.META.get('REMOTE_ADDR')
        self.accept_language = self.request.META.get('HTTP_ACCEPT_LANGUAGE', '')

    def set_local_time(self, datetime):
        self.local_hour = datetime.hour
        self.local_minute = datetime.minute
        self.local_second = datetime.second

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
        url  = self.get_current_scheme() + '://'
        url += self.get_current_host()
        url += self.get_current_script_name()
        url += self.get_current_query_string()
        return url

    def get_timestamp(self):
        return datetime.datetime.now()

    def get_query_vars(self, document_title=False):
        url = "?idsite=%d&rec=1&apiv=%s&r=%s&url=%s&urlref=%s&cip=%s&token_auth=%s" % (
            self.id_site,
            self.VERSION,
            random.randint(0, 99999),
            urllib.quote_plus(self.page_url),
            urllib.quote_plus(self.referer),
            # Forcing IP requires the auth token
            self.ip,
            self.token_auth,
        )
        if document_title:
            url += '&action_name=%s' % urllib.quote_plus(document_title)
        return url

    def send_request(self, query_vars):
        "Send the request to piwik"
        headers = {
            'Accept-Language': self.accept_language,
            'User-Agent': self.user_agent,
        }
        parsed = urlparse.urlparse(self.api_url)
        connection = httplib.HTTPConnection(parsed.hostname)
        url = parsed.path + query_vars
        connection.request('GET', url, '', headers)
        response = connection.getresponse()
        return response.read()

    def do_track_page_view(self, document_title):
        query_vars = self.get_query_vars(document_title)
        return self.send_request(query_vars);

def piwik_get_url_track_page_view(id_site, api_url, request, token_auth, document_title=False):
    tracker = PiwikTracker(id_site, api_url, request, token_auth)
    return tracker.do_track_page_view(document_title)
