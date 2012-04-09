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

You definitely want to create a site specifically for running unit tests
and development in general. In your Piwik install's ``/piwik.php`` set also
this::

    $GLOBALS['PIWIK_TRACKER_DEBUG'] = true;


Some unit tests parse the output of the tracker script. You must create a
``settings`` module somewhere in your Python path that contains a ``Settings``
class like this:

.. autoclass:: piwikapi.tests.settings_sample.Settings
    :members:

If you create that file in the source tree it is also ignored by git for your
convenience.
