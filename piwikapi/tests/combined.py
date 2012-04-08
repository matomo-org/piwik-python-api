from tracking import TrackerBaseTestCase

try:
    from piwikapi.tests.settings import Settings
    settings = Settings()
except:
    raise Exception("You haven't created the necessary Settings class in"
                    "the settings module. This is necessary to run the"
                    "unit tests, please check the documentation.")


class TrackerNoverifyTestCase(TrackerBaseTestCase):
    """
    Here are test we don't verify programmatically yet. I guess we'd have to
    access the Piwik API to fetch data to verify the tracking requests were
    processed properly. At the moment I only check this manually in my Piwik
    dev installation.
    """
    def test_browser_has_cookies(self):
        self.pt.set_browser_has_cookies()
        cookie = "piwiktrackingtest=yes; hascookies=yes"
        self.pt._set_request_cookie(cookie)
        r = self.pt.do_track_page_view(self.get_title('browser has cookie'))
        self.assertTrue(True) # FIXME

    def test_set_resolution(self):
        self.pt.set_token_auth(settings.PIWIK_TOKEN_AUTH) # verify hack
        self.pt.set_resolution(5760, 1080)
        r = self.pt.do_track_page_view(self.get_title('set resolution test'))
        self.assertTrue(True) # FIXME

    def test_set_browser_language(self):
        language = 'de-de'
        self.pt.set_browser_language(language)
        self.assertEqual(
            language,
            self.pt.accept_language,
            "Browser language was not set to %s" % language
        )
        r = self.pt.do_track_page_view(self.get_title('set browser language'))

    def test_set_user_agent(self):
        ua = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.24)' \
            'Gecko/20111103 Firefox/3.6.24'
        self.pt.set_user_agent(ua)
        self.assertEqual(
            ua,
            self.pt.user_agent,
            "User Agent was not set to %s" % ua
        )
        r = self.pt.do_track_page_view(self.get_title('set user agent'))

    def test_custom_variables(self):
        # TODO split this code into the PiwikTracker tests and check if the
        # response body can be used to verify logging
        value = 'quoo'
        self.pt.set_custom_variable(1, 'foo', value, 'page')
        saved = self.pt.get_custom_variable(1, 'page')
        self.assertEqual(
            value,
            saved[1],
            "Custom page variable was not saved, got %s" % saved[1],
        )

        #c = Client()
        url = self.pt.get_request(settings.PIWIK_SITE_ID)
        #print url
        value = 'quoo'
        self.pt.set_custom_variable(1, 'foo', value, 'visit')
        saved = self.pt.get_custom_variable(1, 'visit')
        self.assertEqual(
            value,
            saved[1],
            "Custom visit variable was not saved, got %s" % saved[1],
        )

        action_title = self.get_title('test custom var')
        r = self.pt.do_track_page_view(action_title)

        #print r
