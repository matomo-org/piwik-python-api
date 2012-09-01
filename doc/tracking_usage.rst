Tracking API Usage
==================

If you're not using Django you will have to write some custom wrapper code,
see below. Feel free to send pull request.

.. _usage-without-django:

Usage without Django
--------------------

As this code was written for usage with Django it expects a Django
HttpRequest object in some places. If you're not using Django you'll want to
pass an object that looks like this:

.. autoclass:: piwikapi.tests.request.FakeRequest
    :members:
    :special-members:

You can also have a look at the official Django documentation for the
HttpRequest :ref:`attributes and methods<django:httprequest-attributes>`,
though you'll only need a very small subset of this.

Once you have created a compatible request object you can do this::

    from piwikapi.tracking import PiwikTracker
    import FakeRequest # This is your own class

    headerdict = {
        '<see unit test source or PHP documentation>',
    }

    request = FakeRequest(headerdict)
    pt = PiwikTracker(1, request) # 1 is the Piwik site id
    pt.set_api_url('http://example.com/piwik.php')
    pt.do_track_page_view('Page title')

I think this code is a little odd, but that's how the PHP class was built.

.. _usage-with-django:

Usage with Django
-----------------

In your view code do something like this, assuming you use class based views::

    from piwikapi.tracking import PiwikTracker

    pt = PiwikTracker(1, self.request) # 1 is the Piwik site id
    pt.set_api_url('http://example.com/piwik.php')
    pt.do_track_page_view('Page title')

Basic examples
--------------

These examples assume that you're passing a Django-compatible request object.
If you're not using django see above, :ref:`usage-without-django`.

The first example is probably the easiest thing to track::

    from piwikapi.tracking import PiwikTracker

    pt = PiwikTracker(1, request) # 1 is the side ID you want to log to
    pt.set_api_url('http://yoursite.example.com/piwik.php')
    pt.do_track_page_view("Some page title")

This will log a page view and set the title. The only problem with this is that
the request will be logged to the IP of your server. To avoid this you'll want
to set the auth token of an admin for that site::

    from piwikapi.tracking import PiwikTracker

    pt = PiwikTracker(1, request) # 1 is the side ID you want to log to
    pt.set_api_url('http://yoursite.example.com/piwik.php')
    pt.set_ip('192.0.2.134') # Your visitor's IP
    pt.set_token_auth('YOUR_AUTH_TOKEN_STRING')
    pt.do_track_page_view("Some page title")

That's all, happy tracking!

Please refer to the :ref:`PiwikTracker reference<piwiktracker-reference>`
and :ref:`PiwikTrackerEcommerce reference<piwiktracker-ecommerce-reference>`
for
more information.

..
    Actions
    -------

    There are many examples in the unit test sources. (aka TODO)

    Goals
    -----

    There are many examples in the unit test sources. (aka TODO)

    Ecommerce
    ---------

    There are examples in the unit test sources. (aka TODO)
