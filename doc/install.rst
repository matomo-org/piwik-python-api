Install
=======

You should get the source from github directly for the time being.

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

You need to enable ecommerc tracking inside Piwik, see
http://piwik.org/docs/ecommerce-analytics/#toc-enable-ecommerce-for-the-website

See also :ref:`enable_tracking`.

.. _enable_goal_tracking:

Goal tracking
-------------

It's not possible to create goals through the API, so you will have to
configure your goals through the Piwik web interface before you can track them.

.. _enable_analytics:

Enabling the analytics API
--------------------------

The analytics API works out of the box, no configuration needed.

TODO for public access sites must have anonymous view access, security...

Secure your install
-------------------

First, see :ref:`enable_tracking` and :ref:`enable_analytics` for security
notes specific to the two APIs.

If you use the Pyton API exclusively you could consider password-protecting your
Piwik install with a basic HTTP authentication to add a security layer.
