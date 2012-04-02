class PiwikTracker:
    URL = ''
    VERSION = 1
    LENGTH_VISITOR_ID = 16

    def __init__(self, idSite, apiUrl=False, request):
    	self.cookieSupport = True
    	self.userAgent = False
    	self.localHour = False
    	self.localMinute = False
    	self.localSecond = False
    	self.hasCookies = False
    	self.plugins = False
    	self.visitorCustomVar = False
    	self.pageCustomVar = False
    	self.customData = False
    	self.forcedDatetime = False
    	self.token_auth = False
    	self.attributionInfo = False
    	self.ecommerceLastOrderTimestamp = False
    	self.ecommerceItems = []

    	self.requestCookie = ''
    	self.idSite = idSite
    	self.urlReferrer = False
    	self.pageUrl = self.getCurrentUrl()
    	self.ip = False
    	self.acceptLanguage = False
    	self.userAgent = False
        if apiUrl:
            self.URL = apiUrl
    	self.visitorId = '0123456789abcdef'  #substr(md5(uniqid(rand(), True)), 0, self::LENGTH_VISITOR_ID)

    def set_url(self, url):
        self.pageUrl = url

    def get_current_url(self):
        url  = self.get_current_scheme() + '://'
        url += self.get_current_host()
        url += self.get_current_scriptName()
        url += self.get_current_queryString()
        url += self.get_current_host()
        return url

"""
	/**
	 * If current URL is "http://example.org/dir1/dir2/index.php?param1=value1&param2=value2"
	 * will return "/dir1/dir2/index.php"
	 *
	 * @return string
     * @ignore
	 */
	static protected function getCurrentScriptName()
	{
		$url = '';
		if( !empty($_SERVER['PATH_INFO']) ) {
			$url = $_SERVER['PATH_INFO'];
		}
		else if( !empty($_SERVER['REQUEST_URI']) ) 	{
			if( ($pos = strpos($_SERVER['REQUEST_URI'], '?')) !== false ) {
				$url = substr($_SERVER['REQUEST_URI'], 0, $pos);
			} else {
				$url = $_SERVER['REQUEST_URI'];
			}
		}
		if(empty($url)) {
			$url = $_SERVER['SCRIPT_NAME'];
		}

		if($url[0] !== '/')	{
			$url = '/' . $url;
		}
		return $url;
	}

	/**
	 * If the current URL is 'http://example.org/dir1/dir2/index.php?param1=value1&param2=value2"
	 * will return 'http'
	 *
	 * @return string 'https' or 'http'
     * @ignore
	 */
	static protected function getCurrentScheme()
	{
		if(isset($_SERVER['HTTPS'])
				&& ($_SERVER['HTTPS'] == 'on' || $_SERVER['HTTPS'] === true))
		{
			return 'https';
		}
		return 'http';
	}

	/**
	 * If current URL is "http://example.org/dir1/dir2/index.php?param1=value1&param2=value2"
	 * will return "http://example.org"
	 *
	 * @return string
     * @ignore
	 */
	static protected function getCurrentHost()
	{
		if(isset($_SERVER['HTTP_HOST'])) {
			return $_SERVER['HTTP_HOST'];
		}
		return 'unknown';
	}

	/**
	 * If current URL is "http://example.org/dir1/dir2/index.php?param1=value1&param2=value2"
	 * will return "?param1=value1&param2=value2"
	 *
	 * @return string
     * @ignore
	 */
	static protected function getCurrentQueryString()
	{
		$url = '';
		if(isset($_SERVER['QUERY_STRING'])
			&& !empty($_SERVER['QUERY_STRING']))
		{
			$url .= '?'.$_SERVER['QUERY_STRING'];
		}
		return $url;
	}

	/**
	 * Returns the current full URL (scheme, host, path and query string.
	 *
	 * @return string
     * @ignore
	 */
    static protected function getCurrentUrl()
    {
		return self::getCurrentScheme() . '://'
			. self::getCurrentHost()
			. self::getCurrentScriptName()
			. self::getCurrentQueryString();
	}
}

function Piwik_getUrlTrackPageView( $idSite, $documentTitle = false )
{
	$tracker = new PiwikTracker($idSite);
	return $tracker->getUrlTrackPageView($documentTitle);
"""


x = PiwikTracker(5)
