Analytics API Usage
===================

..
    Basic queries
    -------------

    To retrieve tracking data from today in JSON format::

        from piwikapi.analytics import PiwikAnalytics

        pa = PiwikAnalytics()
        pt.set_api_url('http://yoursite.example.com/piwik.php')
        pa.set_id_site(1) # 1 is the side ID you want to log to
        pa.set_format('json')
        pa.set_period('day')
        pa.set_date('today')

Live data
---------

Here's an example for getting live data for the last five minutes::

    import json
    from piwikapi.analytics import PiwikAnalytics

    pa = PiwikAnalytics()
    pa.set_api_url('http://yoursite.example.com/piwik.php')
    pa.set_id_site(1) # 1 is the side ID you want to log to
    pa.set_format('json')
    pa.set_period('day')
    pa.set_date('today')
    pa.set_method('Live.getLastVisitsDetails')
    pa.set_parameter('lastMinutes', 5)
    visits = json.loads(self.a.send_request())

You can then inspect the data stored in ``visits``. Please refer to the
:ref:`PiwikAnalytics reference<the-piwikanalytics-class>` for more details.

ImageGraphs
-----------

You can also get images from the API, so that you can save them or serve them
to a webbrowser etc.::

    from piwikapi.analytics import PiwikAnalytics

    pa = PiwikAnalytics()
    pa.set_api_url('http://yoursite.example.com/piwik.php')
    pa.set_id_site(1) # 1 is the side ID you want to log to
    pa.set_method('ImageGraph.get')
    pa.set_parameter('apiModule', 'UserCountry')
    pa.set_parameter('apiAction', 'getCountry')
    image = pa.send_request()

..
    Segmentation
    ------------

    There are many examples in the unit test sources. (aka TODO)
