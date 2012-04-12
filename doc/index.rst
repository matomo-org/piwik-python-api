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
   hacking
   hacking_reference
   changelog

About
=====

``python-piwikapi`` is a Python implementation of the Piwik tracking and the
analytics API. You can use it to track visitors, ecommerce, actions, goals,
generate reports and much more. See the official documentation for the PHP and
JavaScript implementations at http://piwik.org/docs/analytics-api/ and
http://piwik.org/docs/tracking-api/ for an overview.

The project is in beta status and the API interface might change in the future.
Get the source from https://github.com/nkuttler/python-piwikapi.

Advantages over client-side logging
-----------------------------------

My first implementation of the Piwik tracking API was written for a client who
needed to track redirects on a Django site. So JavaScript logging obviously
wouldn't work. Doing the tracking API requests from the server instead of the
browser has the big advantage of making it much easier to intertwine business
logic and tracking info.
`Ecommerce <http://piwik.org/docs/ecommerce-analytics/>`_,
`actions and goals <http://piwik.org/docs/tracking-goals-web-analytics/>`_
can be logged without any JavaScript.

Another advantage can be that the browser has one less request to do, and that
you don't depend on any client-side code at all. If you care much about
performance it would probably be a good idea to feed your tracking requests
into some task queue.

Disadvantages
-------------

You can't check all client-side features from the server, such as plugin
support, screen resolution, click goals etc. This could be accomplished by
using some JavaScript code though if necessary.

TODO What happens if we have one client-side request followed only by
server-side requests? Is the info tied to the user/visit?

Analytics API
-------------

The analytics API is used to request tracking reports etc. from a Piwik
installation.

There is also a `different Python implementation
<https://github.com/francois2metz/Python-piwik>`_ of the analytics API.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
