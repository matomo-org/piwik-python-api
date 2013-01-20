Changelog
=========

0.2.2 (2013-01-20)
------------------

- Don't require anonymous view access for unit tests to pass
- Test against Piwik 1.10
- Fix readthedocs build

0.2.1 (2012-10-25)
------------------

- A few small improvements

0.2 (2012-04-15)
----------------

First release as piwikapi on pypi.

- Ecommerce tracking support
- Custom variables tracking support
- Action tracking support
- Goal tracking support
- Added unit tests
- Code refactoring
- Got rid of the Django dependency

0.1 (2012-04-03)
----------------

First release as django-piwik-tracker

- Written in a few hours for a client's project that had just gone live
- Very basic implementation

TODO
----

- Implement and test all the cookie stuff
- Refactor the tracking API code, it's not very pythonic
- Verify all unit tests through the analytics API
- Create sites etc. automatically if necessary for the tests
- TODO: SitesManager plugin
- TODO: ImageGraph plugin
- TODO: UserCountry plugin
- TODO: VisitsSummary plugin
