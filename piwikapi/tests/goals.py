import json

from piwikapi.plugins.goals import PiwikGoals
from ecommerce import TrackerEcommerceBaseTestCase


class GoalsTestCase(TrackerEcommerceBaseTestCase):
    def setUp(self):
        super(GoalsTestCase, self).setUp()

        # Create a test goal
        self.pg = PiwikGoals(self.settings.PIWIK_ANALYTICS_API_URL)
        self.pg.set_format('json')
        r = self.pg.add_goal(
            self.settings.PIWIK_SITE_ID,
            'Auto Goal %s' % self.get_unique_string(),
            'manually',
            'nononono-nevermatchanyting-pattern-this-sucks',
            'contains',
            self.settings.PIWIK_TOKEN_AUTH,
        )
        data = json.loads(r)
        self.goal_id = int(data['value'])

    def tearDown(self):
        # Delete the test goal
        r = self.pg.delete_goal(
            self.settings.PIWIK_SITE_ID,
            self.goal_id,
        )

    def test_track_goal_conversion(self):
        r = self.pte.do_track_goal(self.goal_id)
        self.assertEqual(
            1,
            self.get_v('goalConversions'),
            "Unexpected goalConversions value %s" %
                self.get_v('goalConversions'),
        )

        #for i in (181, ):
        #    print i,
        #    print self.pg.delete_goal(
        #        self.settings.PIWIK_SITE_ID,
        #        i,
        #    )

    def test_create_goal(self):
        """
        This is superfluous as we create a goal on the fly anyway...
        """
        r = self.pg.add_goal(
            self.settings.PIWIK_SITE_ID,
            'Auto Goal %s' % self.get_unique_string(),
            'manually',
            'nononono-nevermatchanyting-pattern-this-sucks',
            'contains',
            self.settings.PIWIK_TOKEN_AUTH,
        )
        data = json.loads(r)
        goal_id = int(data['value'])
        self.assertTrue(
            goal_id > 0,
            "It seems we didn't get a goal ID for the new goal",
        )

        r = self.pg.delete_goal(
            self.settings.PIWIK_SITE_ID,
            goal_id,
        )
        data = json.loads(r)
        self.assertEqual(
            data['result'],
            'success',
            "Couldn't dete goal...",
        )
