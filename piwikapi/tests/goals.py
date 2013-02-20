try:
    import json
except ImportError:
    import simplejson as json

from piwikapi.plugins.goals import PiwikGoals
from ecommerce import TrackerEcommerceBaseTestCase


class GoalsTestCase(TrackerEcommerceBaseTestCase):
    def setUp(self):
        """
        Create a goal unless one was defined in the settings
        """
        super(GoalsTestCase, self).setUp()

        self.pg = PiwikGoals(self.settings['PIWIK_ANALYTICS_API_URL'])
        self.pg.set_format('json')
        if self.settings['PIWIK_GOAL_ID'] is None:
            # Create a test goal
            r = self.pg.add_goal(
                self.settings['PIWIK_SITE_ID'],
                'Auto Goal %s' % self.get_unique_string(),
                'manually',
                'nononono-nevermatchanyting-pattern-this-sucks',
                'contains',
                self.settings['PIWIK_TOKEN_AUTH'],
            )
            data = json.loads(r.decode('utf-8'))
            self.goal_id = int(data['value'])
        else:
            self.goal_id = self.settings['PIWIK_GOAL_ID']

    def tearDown(self):
        if self.settings['PIWIK_GOAL_ID'] is None:
            # Delete the test goal
            r = self.pg.delete_goal(
                self.settings['PIWIK_SITE_ID'],
                self.goal_id,
            )

    def test_track_goal_conversion(self):
        """
        Make sure goal conversions are logged
        """
        #self.pte.set_token_auth(self.settings['PIWIK_TOKEN_AUTH'])
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
        #        self.settings['PIWIK_SITE_ID'],
        #        i,
        #    )

    def test_create_goal(self):
        """
        This is superfluous when we create a goal on the fly
        """
        r = self.pg.add_goal(
            self.settings['PIWIK_SITE_ID'],
            'Auto Goal %s' % self.get_unique_string(),
            'manually',
            'nononono-nevermatchanyting-pattern-this-sucks',
            'contains',
            self.settings['PIWIK_TOKEN_AUTH'],
        )
        data = json.loads(r.decode('utf-8'))
        goal_id = int(data['value'])
        self.assertTrue(
            goal_id > 0,
            "It seems we didn't get a goal ID for the new goal",
        )

        r = self.pg.delete_goal(
            self.settings['PIWIK_SITE_ID'],
            goal_id,
        )
        data = json.loads(r.decode('utf-8'))
        self.assertEqual(
            data['result'],
            'success',
            "Couldn't dete goal...",
        )
