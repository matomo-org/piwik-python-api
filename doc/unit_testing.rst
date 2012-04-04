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

Installing Django
-----------------

This isn't really necessary, the code should be very easy to modify to work
without django.

1. ``pip install django``
2. ``django-admin.py startproject piwikdev``
3. Create a symlink to your ``piwik_tracking`` module inside the project.
4. Edit ``piwikdev/settings.py`` as described in the ``README.rst``

Running the tests
-----------------
Assuming everything went smoothly you should be able to run the unit tests
with
``DJANGO_SETTINGS_MODULE=piwikdev.settings django-admin.py test --failfast piwik_tracking``

Running the tests without Django
--------------------------------
You probably want to create a fake settings module and import that instead
of the one from ``django.conf``. There's already a fake request class that's
used instead of Django Request objects for unit tests.

This code should probably work (untested)::

        class FakeSettings():
                PIWIK_API_URL = '<http://example.com/piwik.php>'
                PIWIK_SITE_ID = <Piwik site id>
                PIWIK_TOKEN_AUTH = '<Piwik auth token>'

        settings = FakeSettings()
