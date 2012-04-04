======
README
======

This is a simplified implementation of the PiwikTracker PHP class.
I didn't need any of the advanced features for my client's project, that's
why I didn't implement everything. The code should be relatively easy to port
to other frameworks or scripts. I only implemented a small subset of the
official API because this app was created for a client who only needs to track
301 and 302 redirects.

Not supported are:

- Ecommerce
- Goals
- Cookies
- JavaScript parameters
- Custom parameters
- ...

It also assumes that the passed request object is a Django HttpRequest. I'm
not really familiar with other frameworks or WSGI in general, but feel free
to send pull requests or contact me for professional support if you'd like to
see more features.

If you work on this code please send me your changes, even if they can't be
merged! I'm interested in packaging this in a way that doesn't depend on
Django.

You'll need to have your own `Piwik <http://piwik.org>`_ installation to send
the tracking requests to.

Usage
-----

Get ``django-piwik-tracking`` into your python path::

    pip install django-piwik-tracking

Add ``piwik_tracking`` to your INSTALLED_APPS in settings.py::

    INSTALLED_APPS = (
        ...,
        'piwik_tracking',
        ...,
    )

Add settings to your ``settings.py`` like this::

        PIWIK_API_URL = '<Your tracker, http://example.com/piwik.php>'
        PIWIK_SITE_ID = <Piwik site id>
        PIWIK_TOKEN_AUTH = '<Piwik auth token>'

In your view code you can do this to track views (FIXME, see unit tests for
example usage)::

    from piwik_tracking.piwiktracker import piwik_get_url_track_page_view
    piwik_get_url_track_page_view(id_site, request, document_title)

Parameters (FIXME)::

- ``id_site``: The Piwik site ID you want to log to
- ``request``: The current request object
- ``document_title``: The title for the current request/view
