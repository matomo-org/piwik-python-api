======
README
======

This is a Python implementation of the Piwik tracking and analytics APIs.

Full Documentation at http://piwikapi.readthedocs.org/en/latest/index.html.

.. image:: https://api.travis-ci.org/piwik/piwik-python-api.png
  :target: https://travis-ci.org/piwik/piwik-python-api

Quickstart
==========

At the moment only Django is supported out of the box. If you use a different
framework/library you'll have to use a fake request class that mimics
Django's. This is easy, but that requirement will be dropped in the future::

    from piwikapi.tracking import PiwikTracker
    from piwikapi.tests.request import FakeRequest

    headers = {
        'HTTP_USER_AGENT': 'Fancy Browser 17.4',
        'REMOTE_ADDR': '203.0.113.4',
        'HTTP_REFERER': 'http://referer.com/somewhere/',
        'HTTP_ACCEPT_LANGUAGE': 'en-US',
        'SERVER_NAME': 'www.example.com',
        'PATH_INFO': '/path/to/page/',
        'QUERY_STRING': 'something=bar',
        'HTTPS': False,
    }
    request = FakeRequest(headers)
    piwiktracker = PiwikTracker(PIWIK_SITE_ID, request)
    piwiktracker.set_api_url(PIWIK_TRACKING_API_URL)
    piwiktracker.set_ip(headers['REMOTE_ADDR']) # Optional, to override the IP
    piwiktracker.set_token_auth(PIWIK_TOKEN_AUTH)  # Optional, to override the IP
    piwiktracker.do_track_page_view('My Page Title')

As you can see the interface is very bad at the moment. This was partially
inherited from the PHP reference implementation, and rewriting the interface is
the next step for this project.

With Django you can skip the FakeRequest and simply pass Django's HttpRequest
object to the API.

News
====

The API code itself isn't very nice, and if I find enough time I'll rewrite it
entirely. It is my intention to continue supporting my old API interface for a
while and to raise deprecation warnings when necessary.

The testing method will change with the 0.3 release. The previous way of using a
setup class won't be supported any more. The project was also moved into the
Piwik project on github, but this shouldn't affect you unless you were checking
out the code from the old repository.

Supported
=========

- Normal tracking
- Custom variables
- Ecommerce
- Goals
- Actions

Not supported yet
=================

- Custom variables through cookies
- Attribution info through cookies
- probably more
