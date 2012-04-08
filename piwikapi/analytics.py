import urllib
import urllib2


class PiwikAnalytics(object):
    """
    The Piwik analytics API class
    """
    #: Stores the parameters for the API query
    p = {}

    def __init__(self):
        "Initalize the object"
        self.set_parameter('module', 'API')
        self.api_url = None

    def set_parameter(self, key, value):
        """
        Set a query parameter

        Args:
            key (str): The parameter to set
            value (mixed): The value you want to set
        """
        self.p[key] = value

    def get_parameter(self, key):
        """
        Get a query parameter

        Args:
            key (str): The parameter to return
        """
        if key in self.p:
            r = p[key]
        else:
            r = None
        return r

    def set_method(self, value):
        self.set_parameter('method', value)

    def set_id_site(self, value):
        self.set_parameter('idSite', value)

    def set_date(self, value):
        self.set_parameter('date', value)

    def set_period(self, value):
        self.set_parameter('period', value)

    def set_format(self, value):
        self.set_parameter('format', value)

    def set_filter_limit(self, value):
        self.set_parameter('filter_limit', value)

    def set_api_url(self, api_url):
        """
        Set which Piwik analytics API URL to use
        """
        self.api_url = api_url

    def get_query_string(self):
        qs = self.api_url
        if self.api_url is None:
            raise Exception("API URL not set")
        if len(self.p):
            qs += '?'
            qs += urllib.urlencode(self.p)
        else:
            pass
        return qs

    def send_request(self):
        """
        Make the analytics API request
        """
        request = urllib2.Request(self.get_query_string())
        response = urllib2.urlopen(request)
        body = response.read()
        return body
