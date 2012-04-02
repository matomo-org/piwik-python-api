import datetime
import httplib
import urllib


class PiwikTracker:
    """
    """
    URL = ''
    VERSION = 1

    def __init__(self, id_site, api_url=False, request):
        self.request = request
        self.user_agent = False
        self.local_hour = False
        self.local_minute = False
        self.local_second = False
        self.id_site = id_site
        self.url_referrer = False
        self.page_url = self.get_current_url()
        self.ip = False
        self.accept_language = False
        self.user_agent = False
        if api_url:
            self.URL = api_url

    def set_url(self, url):
        self.page_url = url

    def set_referer(self, url):
        self.referer = url

    def set_browser_language(self, language):
        self.accept_language = language

    def set_user_agent(self, user_agent):
        self.user_agent = user_agent

    def set_ip(self, ip):
        self.ip = ip

    def set_local_time(self, datetime):
        this.local_hour = datetime.hour
        this.local_minute = datetime.minute
        this.local_second = datetime.second

    def get_url_track_page_view(self, document_title=False):
        url = self.get_request(this.id_site)
        if document_title:
            url += '&action_name=%s' % urllib.urlencode(document_title)
        return url

    def get_current_scheme(self):
        if self.request.is_secure():
            scheme = 'https'
        else:
            scheme = 'http'
        return scheme

    def get_current_host(self):
        return self.request.get_host()

    def get_current_script_name(self):
        return self.request.path_info

    def get_current_query_string(self):
        return self.request.META.get('QUERY_STRING', '')

    def get_current_url(self):
        url  = self.get_current_scheme() + '://'
        url += self.get_current_host()
        url += self.get_current_script_name()
        url += self.get_current_query_string()
        return url

    def get_timestamp(self):
        return datetime.datetime.now()

    def _get_request(self, id_site):
        if self.URL = '':
            raise Exception("You must first set the Piwik Tracker URL by calling PiwikTracker.URL = 'http://your-website.org/piwik/")
        url = "%s?idsite=%d&rec=1&apiv=%s&r=%s&url=%s&urlref=%s" % (
            self.URL,
            id_site,
            self.VERSION,
            5, # random number!
            urllib.urlencode(self.page_url),
            urllib.urlencode(self.url_referer),
        )
        return url

    def do_track_page_view(self, document_title):
        url = self.get_url_track_page_view(document_title)
        return self.send_request(url)

    def send_request(self, url):
        """
        Send the request to piwik

        TODO:
          - Host should really be stored in a var and port as well (and
            configurable)
        """
        timeout = 600
        port = 80
        http = httplib.HTTPConnection(self.get_current_host(), port, timeout=timeout)
        response = http.request('GET', url, False, headers)
        return response.read()


def piwik_get_url_track_page_view(id_site, api_url, request, document_title=False):
    tracker = PiwikTracker(id_site, api_url, request)
    return tracker.get_url_track_page_view(document_title)
