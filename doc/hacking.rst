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

You must create a ``settings`` module somewhere in your Python path that
contains a ``Settings`` class like this:

.. autoclass:: piwikapi.tests.Settings
    :members:

If you create that file in the source tree it is also ignored by git for your
convenience.

Test classes
------------

The unit tests verify that data sent through the API was received by Piwik.
Classes marked with ``Noverify`` do *not* verify this (yet). Verification has
to be done manually through the Piwik interface. It should be possible to
improve this though, by querying the Piwik data API, which hasn't been
implemented in Python yet.

.. autoclass:: piwikapi.tests.TestPiwikTrackerBase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.TestPiwikTracker
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.TestPiwikTrackerNoverify
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.TestPiwikTrackerEcommerceBase
   :members:

.. autoclass:: piwikapi.tests.TestPiwikTrackerEcommerceNoverify
   :members:
   :undoc-members:
