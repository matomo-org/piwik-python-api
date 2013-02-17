try:
    import unittest2 as unittest
except ImportError:
    import unittest

from analytics import AnalyticsClassTestCase
from analytics import AnalyticsTestCase
from analytics import AnalyticsLiveTestCase
from ecommerce import TrackerEcommerceVerifyTestCase
from goals import GoalsTestCase
from tracking import TrackerClassTestCase
from tracking import TrackerVerifyDebugTestCase
from tracking import TrackerVerifyTestCase


if __name__ == '__main__':
    unittest.main()
