Install
=======

You should get the source from github directly for the time being. There is a
django-piwik-tracking pypi package you could install and that works, but you
shouldn't use it :-)

Installing Piwik
----------------

1. Install Piwik, see http://piwik.org/docs/installation-optimization/
2. Create a new development site

.. _enable_tracking:

Enabling the tracking API
-------------------------

For simple tracking you don't need to do anything. However, by default all
tracking requests will originate from your server.

If you want your user's IP to be logged (you probably do) create a new user
and make that user an admin of the site you want to track.

.. _enable_ecommerce_tracking:

.. _enable_analytics:

Enabling the analytics API
--------------------------

There's nothing to do here.

Enabling ecommerce tracking
---------------------------

You need to enable ecommerc tracking inside Piwik, see
http://piwik.org/docs/ecommerce-analytics/#toc-enable-ecommerce-for-the-website

See also :ref:`enable_tracking`.
