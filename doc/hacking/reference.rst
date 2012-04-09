Test classes reference
======================

The unit tests verify that data sent through the API was received by Piwik.
Classes marked with ``Noverify`` do *not* verify this (yet). Verification has
to be done manually through the Piwik interface. It should be possible to
improve this though, by querying the Piwik analytics API, which hasn't been
implemented in Python yet.

Base
----

.. autoclass:: piwikapi.tests.base.PiwikAPITestCase
   :members:
   :undoc-members:

Analytics API tests
-------------------

.. autoclass:: piwikapi.tests.analytics.AnalyticsBaseTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.analytics.AnalyticsTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.analytics.AnalyticsLiveBaseTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.analytics.AnalyticsLiveTestCase
   :members:
   :undoc-members:


Tracking API tests
------------------

.. autoclass:: piwikapi.tests.tracking.TrackerBaseTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.tracking.TrackerClassTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.tracking.TrackerTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.tracking_verified.TrackerVerifyBaseTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.tracking_verified.TrackerVerifyTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.ecommerce.TrackerEcommerceBaseTestCase
   :members:

.. autoclass:: piwikapi.tests.ecommerce.TrackerEcommerceNoverifyTestCase
   :members:
   :undoc-members:
