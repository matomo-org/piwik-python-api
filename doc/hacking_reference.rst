Test classes reference
======================

The unit tests verify that data sent through the API was received by Piwik,
either by parsing the debug output or by querying the analytics API.

Analytics API tests
-------------------

These are just some very simple tests. The real testing happens in the
tracking API tests, where the analytics API is used to verify the submitted
data.

.. autoclass:: piwikapi.tests.analytics.AnalyticsTestCase
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

.. autoclass:: piwikapi.tests.tracking.TrackerVerifyDebugTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.tracking.TrackerVerifyBaseTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.tracking.TrackerVerifyTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.ecommerce.TrackerEcommerceBaseTestCase
   :members:
   :undoc-members:

.. autoclass:: piwikapi.tests.ecommerce.TrackerEcommerceVerifyTestCase
   :members:
   :undoc-members:

Plugin tests
------------

.. autoclass:: piwikapi.tests.goals.GoalsTestCase
   :members:
   :undoc-members:
