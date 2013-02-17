.. piwikapi documentation master file, created by
   sphinx-quickstart on Thu Apr  5 10:25:54 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

About
=====

.. image:: pic/piwik_logo.jpg
   :alt: Piwik
   :align: right

``piwikapi`` is a Python implementation of the Piwik tracking and the
analytics API. You can use it to track visitors, ecommerce, actions, goals,
generate reports and much more.

The package was originally written for Django and expects a Django HttpRequest
object. However, you don't need to use Django, you can create a
:ref:`mockup object<usage-without-django>` instead.

As ``piwikapi`` only implements a Python interface to the Piwik APIs
you'll want to check their official documentation as well.

Tracking API:

- http://piwik.org/docs/tracking-api/
- http://piwik.org/docs/tracking-api/reference/
- http://piwik.org/docs/tracking-goals-web-analytics/

Analytics API:

- http://piwik.org/docs/analytics-api/
- http://piwik.org/docs/ecommerce-analytics/
- http://piwik.org/docs/analytics-api/reference/
- http://piwik.org/docs/analytics-api/segmentation/
- http://piwik.org/docs/analytics-api/metadata/

Misc:

- http://piwik.org/docs/custom-variables/

The project is in alpha status and the API interface might change in the
future. The full source is available at
https://github.com/piwik/piwik-python-api.

Advantages over client-side tracking
------------------------------------
My first implementation of the Piwik tracking API was written for a client who
needed to track 301 and 302 redirects on a Django site. So JavaScript logging
obviously wouldn't work. Doing the tracking API requests from the server
instead of the browser has the big advantage of making it much easier to
intertwine business logic and tracking info.
`Ecommerce <http://piwik.org/docs/ecommerce-analytics/>`_,
`actions and goals <http://piwik.org/docs/tracking-goals-web-analytics/>`_ can
be logged without any JavaScript.

Another advantage can be that the browser has one less request to do, and that
you don't depend on any client-side code at all. If you care much about
performance it would probably be a good idea to feed your tracking requests
into some task queue.

Disadvantages
-------------
You can't check all client-side features from the server, such as plugin
support, screen resolution, click goals etc. This could be accomplished by
using some JavaScript code though if necessary.

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
entirely. It is my intention to continue supporting the old API interface for a
while and to raise deprecation warnings when necessary.

The testing method will change with the 0.3 release. The previous way of using a
setup class won't be supported any more. The project was also moved into the
Piwik project on github, but this shouldn't affect you unless you were checking
out the code from the old repository.

Todo
====
- Abstraction for various request models (Django, webob, ...?)
- API rewrite
- CLI client (?)

Supported
---------
- Normal tracking
- Custom variables
- Ecommerce
- Goals
- Actions

Not supported yet
-----------------
- Custom variables through cookies
- Attribution info through cookies
- probably more

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::

   install
   tracking_usage
   tracking_reference
   analytics_usage
   analytics_reference
   plugins_reference
   hacking
   hacking_reference
   changelog

..
    TODO What happens if we have one client-side request followed only by
    server-side requests? Is the info tied to the user/visit?

    Analytics API
    -------------

    The analytics API is used to request tracking reports etc. from a Piwik
    installation.

    There is also a `different Python implementation
    <https://github.com/francois2metz/Python-piwik>`_ of the analytics API.

    There's also a class for the Piwik analytics API, but it's very rudimentary at
    the moment. It was written for unit testing, to verify that the data sent
    through the tracking API was logged by Piwik.

