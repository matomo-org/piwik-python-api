.. python-piwikapi documentation master file, created by
   sphinx-quickstart on Thu Apr  5 10:25:54 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-piwikapi's documentation!
===========================================

.. image:: pic/piwik_logo.jpg
   :alt: Piwik
   :align: right

Contents:

.. toctree::
   :maxdepth: 3

   install
   tracking_usage
   tracking_reference
   analytics_usage
   analytics_reference
   plugins_reference
   hacking
   hacking_reference
   changelog

About
=====

``python-piwikapi`` is a Python implementation of the Piwik tracking and the
analytics API. You can use it to track visitors, ecommerce, actions, goals,
generate reports and much more.

The package was originally written for Django and expects a Django HttpRequest
object. However, you don't need to use Django, you can create a
:ref:`mockup object<usage-without-django>` instead.

As ``python-piwikapi`` only implements a Python interface to the Piwik APIs
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
https://github.com/nkuttler/python-piwikapi.

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

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

