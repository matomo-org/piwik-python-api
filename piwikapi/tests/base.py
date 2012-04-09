import pprint
import unittest

try:
    from settings import Settings
    settings = Settings()
except:
    raise Exception("You haven't created the necessary Settings class in"
                    "the settings module. This is necessary to run the"
                    "unit tests, please check the documentation.")


class PiwikAPITestCase(unittest.TestCase):
    """
    The base class for all test classes

    Provides a fake request, PiwikTracker and PiwikTrackerEcommerce instances.
    """
    def setUp(self):
        self.settings = Settings()

    def debug(self, value):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(value)
