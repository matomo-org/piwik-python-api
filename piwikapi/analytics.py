import urllib
import urllib2


class PiwikAnalytics(object):
    """
    The Piwik analytics API class
    """
    #: Stores the parameters for the API query
    p = {}

    def __init__(self):
        """
        Initalize the object

        :rtype: None
        """
        self.set_parameter('module', 'API')
        self.api_url = None

    def set_parameter(self, key, value):
        """
        Set a query parameter

        :param key: The parameter to set
        :type key: str
        :param value: The value you want to set
        :type value: TODO, str?
        :rtype: None
        """
        self.p[key] = value

    def get_parameter(self, key):
        """
        Get a query parameter

        :param key: The parameter to return
        :type key: str
        :rtype: TODO mixed?
        """
        if key in self.p:
            r = p[key]
        else:
            r = None
        return r

    def set_method(self, method):
        """
        :param method: Method
        :type method: str
        :rtype: None
        """
        self.set_parameter('method', method)

    def set_id_site(self, id_site):
        """
        :param id_site: Site ID
        :type id_site: int
        :rtype: None
        """
        self.set_parameter('idSite', id_site)

    def set_date(self, date):
        """
        :param date: Date string TODO format
        :type date: str
        :rtype: None
        """
        self.set_parameter('date', date)

    def set_period(self, period):
        """
        :param period: Period TODO optinos
        :type period: str
        :rtype: None
        """
        self.set_parameter('period', period)

    def set_format(self, format):
        """
        :param format: Format TODO
        :type format: str
        :rtype: None
        """
        self.set_parameter('format', format)

    def set_filter_limit(self, filter_limit):
        """
        :param filter_limit: Filter limit TODO
        :type filter_limit: TODO ?
        :rtype: None
        """
        self.set_parameter('filter_limit', filter_limit)

    def set_api_url(self, api_url):
        """
        :param api_url: Piwik analytics API URL, the root of your Piwik install
        :type api_url: str
        :rtype: None
        """
        self.api_url = api_url

    def set_segment(self, segment):
        """
        :param segment: Which segment to request, see
            http://piwik.org/docs/analytics-api/segmentation/
        :type segment: str
        :rtype: None
        """
        self.set_parameter('segment', segment)

    def get_query_string(self):
        """
        Return the query string

        :rtype: str
        """
        if self.api_url is None:
            raise Exception("API URL not set")
        if len(self.p):
            qs = self.api_url
            qs += '?'
            qs += urllib.urlencode(self.p)
        else:
            pass
        return qs

    def send_request(self):
        """
        Make the analytics API request, returns the request body

        :rtype: str
        """
        request = urllib2.Request(self.get_query_string())
        response = urllib2.urlopen(request)
        body = response.read()
        return body
