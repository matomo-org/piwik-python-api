Install
=======

Installing the API
------------------

You can get the source from https://github.com/piwik/piwik-python-api or
install it with pip::

    pip install piwikapi

On Python 2.5 you'll also have to install `simplejson
<http://pypi.python.org/pypi/simplejson/>`_.

Installing Piwik
----------------

To install Piwik please see http://piwik.org/docs/installation-optimization/.

.. _enable_tracking:

Enabling the tracking API
-------------------------

For simple tracking you don't need to do anything. However, by default all
tracking requests will originate from your server.

If you want your user's IP to be logged (you probably do) create a new user
and make that user an admin of the site you want to track.

Keep in mind that the auth token will be submitted with each request, so you
should consider using SSL to submit the data to your server.

.. _enable_ecommerce_tracking:

Enabling ecommerce tracking
---------------------------

You need to enable ecommerce tracking inside Piwik, see
http://piwik.org/docs/ecommerce-analytics/#toc-enable-ecommerce-for-the-website

See also :ref:`enable_tracking`.

If you want to track goals you'll have to create them first. Either through the
web interface or the API.

.. _enable_analytics:

Enabling the analytics API
--------------------------

The analytics API works out of the box, no configuration is needed. To view
reports the viewer must have access. You could just give anonymous access to
the data but it's probably better to use the auth token.

Secure your install
-------------------

First you should check the official docs at
http://piwik.org/security/how-to-secure-piwik/.

If you use the Python API exclusively you could consider password-protecting your
Piwik install or binding the httpd to local interfaces only etc.
