Unit testing
============

If you want to work on the code you should have a look at the original
``PiwikTracking.php`` in the Piwik source tree. There's also a
``PiwikTracking.java`` implementation in the release.

Configuring Piwik
-----------------

1. Install Piwik
2. Create a new development site
3. Create a new user
4. Make that user an admin of the development site
5. Set ``$GLOBALS['PIWIK_TRACKER_DEBUG']`` to ``true`` in ``/piwik.php``

Running the tests without Django
--------------------------------
You probably want to create a fake settings module that will be used
instead of the one from ``django.conf``. There's already a fake request
class that's used instead of Django Request objects for the unit tests.

Using this code in ``piwik_tracking/fake_settings.py`` should work::

        class FakeSettings:
                PIWIK_API_URL = 'http://example.com/piwik.php'
                PIWIK_SITE_ID = '<Piwik site id>'
                PIWIK_TOKEN_AUTH = '<Piwik auth token>'

That file is also ignored by git for your convenience.

Running the tests with Django
-----------------------------
The easiest is probably to create a symlink to your working copy of the
``piwik_tracking`` module inside your project. You should be able to run the
unit tests with the usual ``manage.py test --failfast piwik_tracking``.
Don't forget to configure the app as described in the ``README.rst``.
