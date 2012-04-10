Hacking
=======

.. toctree::
   :maxdepth: 2

   reference

If you want to work on the tracking code you should have a look at the original
``PiwikTracking.php`` in the Piwik source tree. There's also a
``PiwikTracking.java`` implementation in the release.

Running the unit tests
----------------------

To run the unit tests you need to:

- Create a new Piwik site
- Create a goal
- Create a settings module
- Enable tracker debugging

You want to create a **new site** specifically for running the unit tests as to
not pollute a real site with test data.

You have to create **one goal** for the unit tests to pass. This has to be done
in the web interface, it can't be automated.

You must create a ``settings`` **module** somewhere in your Python path that
contains a ``Settings`` class like this:

.. autoclass:: piwikapi.tests.settings_sample.Settings
    :members:

If you create the settings file in the test source directory it is also
ignored by ``git`` for your convenience.

Some unit tests parse the output of the tracker script, so you have to **enable
debugging** in your Piwik install's ``/piwik.php``::

    $GLOBALS['PIWIK_TRACKER_DEBUG'] = true;
