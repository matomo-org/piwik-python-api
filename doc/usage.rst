Usage
=====

You have to install and configure Piwik first. If you're not using Django you
will also have to write some custom wrapper code, see below. Feel free to
send pull request.

Configuring Piwik
-----------------

1. Install Piwik
2. Create a new development site
3. Create a new user
4. Make that user an admin of the development site. If you don't do this the
   remote IP won't be logged.

.. _usage-without-django:

Usage without Django
--------------------

As this code was written for usage with Django it expects a Django
HttpRequest object in some places. If you're not using Django you'll want to
pass an object that looks like this:

.. autoclass:: piwiktracking.tests.FakeRequest
    :members:

You can also have a look at the official Django documentation for the
HttpRequest :ref:`attributes and methods<django:httprequest-attributes>`,
though you'll only need a small subset of this.

Once you have created a compatible request object you can do this::

    from piwik_tracker import PiwikTracker

    headerdict = {
        '<see unit test source or PHP documentation>',
    }

    request = FakeRequest(headerdict)
    pt = PiwikTracker(1, request) # 1 is the Piwik site id
    pt.set_api_url('http://example.com/piwik.php')
    pt.do_track_page_view('Page title')

Yes, this code is a little odd but that's how the PHP class was built. I
will probably refactor the code in the future and break compatibility.

.. _usage-with-django:

Usage with Django
-----------------

In your view code do something like this, assuming you use class based views::

    from piwik_tracker import PiwikTracker

    pt = PiwikTracker(1, self.request) # 1 is the Piwik site id
    pt.set_api_url('http://example.com/piwik.php')
    pt.do_track_page_view('Page title')
