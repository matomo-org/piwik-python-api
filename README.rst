======
README
======

This is a piwik tracking API implementation for django. The code should be
easy to port to other frameworks or scripts.

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

Add settings just as::

    PIWIK_TRACKING = <piwik-site-id>

TODO support sites framework
