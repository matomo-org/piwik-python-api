"""
Copyright (c) 2012-2013, Nicolas Kuttler.
All rights reserved.

License: BSD, see LICENSE for details

Source and development at https://github.com/piwik/piwik-python-api
"""

from piwikapi.analytics import PiwikAnalytics


class PiwikGoals(PiwikAnalytics):
    def __init__(self, api_url):
        """
        Initialize a PiwikAnalytics object

        :param api_url: Piwik API url, root of the install
        :type api_url: str
        :rtype: None
        """
        super(PiwikGoals, self).__init__()
        self.set_api_url(api_url)

    def add_goal(self, id_site, name, match_attribute, pattern,
                 pattern_type, token_auth, case_sensitive=False, revenue=False,
                 allow_multiple_conversions_per_visits=False):
        """
        Create a goal

        :param id_site: Site ID
        :param name: Name of the goal
        :param match_attribute: 'url', 'title', 'file', 'external_website'
            or 'manually'
        :param pattern: eg. purchase-confirmation.htm
        :param pattern_type': 'regex', 'contains', 'exact'
        :param case_sensitive: Case sensitive
        :type case_sensitive: bool
        :param revenue: Revenue per action
        :type reveneue: float or str
        :param allow_multiple_conversions_per_visits: By default, multiple
            conversions in the same visit will only record the first
            conversion. If set to true, multiple conversions will all be
            recorded within a visit (useful for Ecommerce goals)
        :type allow_multiple_conversions_per_visits: bool
        :rtype: int, ID of the new goal
        """
        self.set_method('Goals.addGoal')
        self.set_id_site(id_site)
        self.set_parameter('name', name)
        self.set_parameter('matchAttribute', match_attribute)
        self.set_parameter('pattern', pattern)
        self.set_parameter('patternType', pattern_type)
        self.set_parameter('token_auth', token_auth)
        return self.send_request()

    def delete_goal(self, id_site, id_goal):
        """
        Delete a goal

        :param id_site: Site ID
        :param id_goal: Goal ID
        """
        self.set_method('Goals.deleteGoal')
        self.set_id_site(id_site)
        self.set_parameter('idGoal', id_goal)
        return self.send_request()
