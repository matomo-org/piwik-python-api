Hacking
=======

If you want to work on the code you should have a look at the original
``PiwikTracking.php`` in the Piwik source tree. There's also a
``PiwikTracking.java`` implementation in the release.

Running the unit tests
----------------------

You definitely want to create a site specifically for running unit tests
and development in general. In your Piwik install's ``/piwik.php`` set also
this::

    $GLOBALS['PIWIK_TRACKER_DEBUG'] = true;

You probably want to create a fake settings module that will be used
instead of the one from ``django.conf``. There's already a fake request
class that's used instead of Django Request objects for the unit tests.

Using this code in ``piwiktracking/fake_settings.py`` should work::

    class FakeSettings:
            PIWIK_API_URL = 'http://example.com/piwik.php'
            PIWIK_SITE_ID = '<Piwik site id>'
            PIWIK_TOKEN_AUTH = '<Piwik auth token>'

That file is also ignored by git for your convenience.

Test classes
------------

.. autoclass:: piwiktracking.tests.TestPiwikTrackerBase
   :members:

.. autoclass:: piwiktracking.tests.TestPiwikTracker
   :members:

.. autoclass:: piwiktracking.tests.TestPiwikTrackerNoverify
   :members:

.. autoclass:: piwiktracking.tests.TestPiwikTrackerEcommerceBase
   :members:

.. autoclass:: piwiktracking.tests.TestPiwikTrackerEcommerceNoverify
   :members:
