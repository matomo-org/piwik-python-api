#!/usr/bin/env python

u"""
Copyright (c) 2012-2013, Nicolas Kuttler.
All rights reserved.

License: BSD, see LICENSE for details

Source and development at https://github.com/piwik/piwik-python-api
"""

import os
import sys
import datetime
import math
import logging
import random
import string
import hashlib
from uuid import UUID
from decimal import Decimal
from pprint import pprint
try:
    import json
except ImportError:
    import simplejson as json
import urllib3

import requests

from .exceptions import ConfigurationError
from .exceptions import InvalidParameter
from .types import check, to_string


class PiwikTracker(object):
    u"""
    The Piwik tracker class
    """
    ## Piwik API version
    VERSION = 1

    ## Length of the visitor ID
    LENGTH_VISITOR_ID = 16

    ## List of plugins Piwik knows
    KNOWN_PLUGINS = {
        u"flash": u"fla",
        u"java": u"java",
        u"director": u"dir",
        u"quick_time": u"qt",
        u"real_player": u"realp",
        u"pdf": u"pdf",
        u"windows_media": u"wma",
        u"gears": u"gears",
        u"silverlight": u"ag"
    }

    UNSUPPORTED_WARNING = (
        u"%s: The code that is just running is untested and "
        u"probably does not work as expected anyway."
    )

    page_titles = None
    ecommerce_items = None
    id_site = None
    api_url = None
    request_cookie = None
    user_agent = None
    accept_language = None
    ip = None
    referer = None
    token_auth = None
    local_time = None
    forced_datetime = None
    local_time = None
    page_url = None
    has_cookies = None
    width = None
    height = None
    visitor_id = None
    debug_append_url = None
    event_custom_var = None
    page_custom_var = None
    event_tracking = None
    action_tracking = None
    search_tracking = None
    content_tracking = None
    visitor_custom_var = None
    dimensions = None
    plugins = None
    attribution_info = None
    user_id = None
    send_image = None
    goal = None
    debug = None
    ecomm_order = None
    ssl_verify = None

    def __init__(self, id_site):
        u"""
        :param id_site: Site ID
        :type id_site: int
        :param request: Request
        :type request: A Django-like request object
        :rtype: None
        """
        check(id_site, [int])
        random.seed()
        self.page_titles = None
        self.ecommerce_items = {}
        self.id_site = id_site
        self.api_url = None
        self.request_cookies = None
        self.user_agent = None
        self.accept_language = None
        self.ip = None
        self.referer = None
        self.token_auth = None
        self.forced_datetime = None
        self.local_time = None
        self.page_url = None
        self.has_cookies = False
        self.width = None
        self.height = None
        self.visitor_id = None
        self.debug_append_url = False
        self.event_custom_var = None
        self.page_custom_var = None
        self.visitor_custom_var = None
        self.event_tracking = None
        self.action_tracking = None
        self.search_tracking = None
        self.content_tracking = None
        self.dimensions = None
        self.plugins = None
        self.attribution_info = None
        self.user_id = None
        self.send_image = False
        self.goal = None
        self.debug = False
        self.ecomm_order = None
        self.ssl_verify = True
        return

    def set_local_time(self, dt):
        u"""
        Set the time

        :param datetime: Time
        :type datetime: datetime.datetime object
        :rtype: bool
        """
        check(dt, [datetime.datetime])
        self.local_time = dt
        return True

    def set_token_auth(self, token_auth):
        u"""
        Set the auth token for the request. The token can be viewed in the
        user management section of your Piwik install.

        :param token_auth: Auth token
        :type token_auth: str
        :rtype: bool
        """
        check(token_auth, [u"string"])
        self.token_auth = token_auth
        return True

    def set_api_url(self, api_url):
        u"""
        Set which Piwik API URL to use

        :param api_url: API URL
        :type api_url: str
        :rtype: bool
        """
        check(api_url, [u"string"])
        self.api_url = api_url
        return True

    def set_ip(self, ip):
        u"""
        Set the IP to be tracked. You probably want to use this as the
        request comes from your own server.

        Requires setting the auth token.

        :param ip: IP
        :type ip: str
        :rtype: bool
        """
        check(ip, [u"string"])
        self.ip = ip
        return True

    def set_browser_has_cookies(self):
        u"""
        Call this is the browser supports cookies

        :rtype: bool
        """
        self.has_cookies = True
        return True

    def set_browser_language(self, language):
        u"""
        Set the browser language. Piwik uses this to guess the visitor"s
        origin when GeoIP is not enabled

        :param language: Accept-Language
        :type language: str
        :rtype: bool
        """
        check(language, [u"string"])
        self.accept_language = language
        return True

    def set_user_agent(self, user_agent):
        u"""
        Set the user agent. By default the original request"s UA is used.

        :param user_agent: User agent
        :type user_agent: str
        :rtype: bool
        """
        check(user_agent, [u"string"])
        self.user_agent = user_agent
        return True

    def set_resolution(self, width, height):
        u"""
        Set the visitor"s screen width and height

        :param width: Screen width
        :type width: int or str
        :param height: Screen height
        :type height: int or str
        :rtype: bool
        """
        check(width, [int])
        check(height, [int])
        self.width = width
        self.height = height
        return True

    def set_new_visitor_id(self):
        u"""
        Sets the current visitor ID to a random new one.
        """
        self.visitor_id = self.build_random_visitor_id()
        return True

    def set_visitor_id(self, visitor_id):
        u"""
        Set the visitor's unique User ID. See https://piwik.org/docs/user-id/

        :param visitor_id: Visitor I
        :type visitor_id: str
        :raises: InvalidParameter if the visitor_id has an incorrect length
        :rtype: bool
        """
        check(visitor_id, [u"string"])
        if len(visitor_id) != self.LENGTH_VISITOR_ID:
            raise InvalidParameter(
                u"set_visitor_id() expects a visitor ID of "
                u"length %s" % self.LENGTH_VISITOR_ID
            )
        self.visitor_id = visitor_id
        return True

    def set_visitor_id_hash(self, orig_visitor_id):
        check(visitor_id, [u"string"])
        self.visitor_id = (
            hashlib
            .sha512(
                orig_visitor_id.encode(u"utf8")
            )
            .hexdigest()[:16]
            .upper()
        )
        return True

    def set_user_id(self, user_id):
        u"""
        Force the action to be recorded for a specific User.

        :param user_id:
            The User ID is a string representing a given user in your system.
            A User ID can be a username, UUID or an email address, or any number
            or string that uniquely identifies a user or client.
        :rtype: bool
        """
        check(user_id, [u"string", int])
        self.user_id = user_id
        return True

    def set_user_id_hash(self, orig_user_id):
        u"""
        Force the action to be recorded for a specific User.

        :param user_id:
            The User ID is a string representing a given user in your system.
            A User ID can be a username, UUID or an email address, or any number
            or string that uniquely identifies a user or client.
        :rtype: bool
        """
        check(user_id, [u"string", int])
        self.user_id = (
            str(
                UUID(
                    hashlib.sha512(
                        orig_user_id.encode(u"UTF-8")
                    )
                    .hexdigest()[0:32]
                )
            )
        )
        return True

    def set_send_image_response(self, should_send):
        u"""
        If image response is disabled Piwik will respond with a
        HTTP 204 header instead of responding with a gif.

        :rtype: bool
        """
        check(should_send, [bool])
        self.send_image = should_send
        return True

    def set_debug(self, should_debug):
        u"""
        :param string: str to append
        :type string: str
        :rtype: bool
        """
        self.debug = should_debug
        return True

    def set_url_referer(self, referer):
        u"""
        Set the referer URL

        :param referer: Referer
        :type referer: str
        :rtype: bool
        """
        self.referer = referer
        return True

    def set_url(self, url):
        u"""
        Set URL being tracked

        :param url: URL
        :type url: str
        :rtype: bool
        """
        self.page_url = url
        return True

    def set_attribution_info(
            self,
            campaign_name,
            campaign_keyword,
            referral_datetime,
            referral_url
    ):
        u"""
        Set the attribution info for the visit, so that subsequent goal
        conversions are properly attributed to the right referer, timestamp,
        campaign name and keyword.

        This must be a JSON encoded string that you would normally fetch from
        the Javascript API, see function getAttributionInfo() in
        http://dev.piwik.org/trac/browser/trunk/js/piwik.js

        :param json_encoded: JSON encoded list containing attribution info
        :type json_encoded: string
        :raises: InvalidParameter if the json_encoded data is incorrect
        :rtype: bool
        """
        check(campaign_name, [u"string"])
        check(campaign_keyword, [u"string"])
        check(campaign_datetime, [datetime.datetime])
        check(campaign_url, [u"string"])
        self.attribution_info = {
            u"campaign_name": campaign_name,
            u"campaign_keyword": campaign_keyword,
            u"referral_datetime": referral_datetime,
            u"referral_url": referral_url
        }
        return True

    def set_force_visit_date_time(self, dt):
        u"""
        Override the server date and time for the tracking request.

        By default Piwik tracks requests for the "current" datetime, but
        this method allows you to track visits in the past. Time are in
        UTC.

        Requires setting the auth token.

        :param datetime: datetime
        :type datetime: datetime.datetime object
        :rtype: bool
        """
        check(dt, [datetime.datetime])
        self.forced_datetime = datetime
        return True

    def _get_request(self):
        u"""
        This oddly named method returns the query var string.

        :param id_site: Site ID
        :type id_site: int
        :rtype: str
        """
        query_vars = {}
        query_vars[u"idsite"] = to_string(self.id_site)
        query_vars[u"rec"] = to_string(1)
        query_vars[u"url"] = self.page_url
        query_vars[u"apiv"] = to_string(self.VERSION)
        query_vars[u"rand"] = to_string(random.randint(0, 99999))
        if self.referer is not None:
            query_vars[u"referer"] = self.referer
        if self.page_titles is not None:
            query_vars[u"action_name"] = "/".join(self.page_titles)
        if self.local_time is not None:
            query_vars[u"h"] = to_string(self.local_time.hour)
            query_vars[u"m"] = to_string(self.local_time.minute)
            query_vars[u"s"] = to_string(self.local_time.second)
        if self.ip is not None:
            query_vars[u"cip"] = self.ip
        if self.token_auth is not None:
            query_vars[u"token_auth"] = self.token_auth
        if self.has_cookies:
            query_vars[u"cookie"] = to_string(1)
        if self.width is not None and self.height is not None:
            query_vars[u"res"] = u"%dx%d" % (self.width, self.height)
        if self.visitor_id is not None:
            query_vars[u"cid"] = self.visitor_id
            #query_vars[u"_id"] = self.visitor_id
        if self.user_id is not None:
            query_vars[u"uid"] = to_string(self.user_id)
        if self.send_image is not None:
            query_vars[u"send_image"] = to_string(1 if self.send_image else 0)
        if self.event_custom_var is not None:
            query_vars[u"e_cvar"] = json.dumps(self.event_custom_var)
        if self.page_custom_var is not None:
            query_vars[u"cvar"] = json.dumps(self.page_custom_var)
        if self.visitor_custom_var is not None:
            query_vars[u"_cvar"] = json.dumps(self.visitor_custom_var)
        if self.event_tracking is not None:
            query_vars[u"e_c"] = self.event_tracking[u"category"]
            query_vars[u"e_a"] = self.event_tracking[u"action"]
            if self.event_tracking[u"name"] is not None:
                query_vars[u"e_n"] = self.event_tracking[u"name"]
            if self.event_tracking[u"value"] is not None:
                query_vars[u"e_v"] = to_string(self.event_tracking[u"value"])
        if self.dimensions is not None:
            for dim_key, dim_val in self.dimensions.items():
                query_vars["dimension%s" % dim_key] = to_string(dim_val)
        if self.plugins is not None:
            for plugin, version in self.plugins.items():
                query_vars[plugin] = to_string(version)
        if self.attribution_info is not None:
            query_vars[u"_rcn"] = self.attribution_info[u"campaign_name"]
            query_vars[u"_rck"] = self.attribution_info[u"campaign_keyword"]
            query_vars[u"_refts"] = (
                to_string(
                    math.floor(
                        self.attribution_info[u"referral_datetime"].timestamp()
                    )
                )
            )
            query_vars[u"_ref"] = self.attribution_info[u"referral_url"]
        if self.action_tracking is not None:
            if self.action_tracking[u"type"] == u"download":
                query_vars[u"download"] = self.action_tracking[u"url"]
            if self.action_tracking[u"type"] == u"link":
                query_vars[u"link"] = self.action_tracking[u"url"]
        if self.goal is not None:
            query_vars[u"idgoal"] = to_string(self.goal[u"id"])
            if u"revenue" in self.goal:
                query_vars[u"revenue"] = to_string(self.goal[u"revenue"])
        if self.search_tracking is not None:
            query_vars[u"search"] = self.search_tracking[u"query"]
            if u"category" in self.search_tracking:
                query_vars[u"search_cat"] = self.search_tracking[u"category"]
            if u"count" in self.search_tracking:
                query_vars[u"search_count"] = (
                    to_string(self.search_tracking[u"count"])
                )
        if self.content_tracking is not None:
            query_vars[u"c_n"] = self.content_tracking[u"name"]
            query_vars[u"c_p"] = self.content_tracking[u"value"]
            query_vars[u"c_t"] = self.content_tracking[u"target"]
            query_vars[u"c_p"] = to_string(self.content_tracking[u"value"])
        if self.ecomm_order is not None:
            if u"id" in self.ecomm_order:
                query_vars[u"ec_id"] = to_string(self.ecomm_order[u"id"])
            if u"sub_total" in self.ecomm_order:
                query_vars[u"ec_st"] = to_string(self.ecomm_order[u"sub_total"])
            if u"tax" in self.ecomm_order:
                query_vars[u"ec_tx"] = to_string(self.ecomm_order[u"tax"])
            if u"dt" in self.ecomm_order:
                query_vars[u"ec_dt"] = to_string(self.ecomm_order[u"discount"])
            if u"track_datetime" in self.ecomm_order:
                query_vars[u"_ects"] = (
                    to_string(
                        math.floor(self.ecomm_order[u"track_datetime"].timestamp())
                    )
                )
            if u"items" in self.ecomm_order:
                query_vars[u"ec_items"] = (
                    json.dumps(
                        list(
                            map(
                                lambda r: (
                                    r[u"sku"],
                                    r[u"name"],
                                    r[u"category"],
                                    r[u"price"],
                                    r[u"quantity"]
                                ),
                                self.ecomm_order[u"items"]
                            )
                        )
                    )
                )
        if self.debug is True:
            query_vars[u"debug"] = to_string(1)
        return query_vars

    def set_track_content(
            self,
            name,
            interaction,
            value=None,
            target=None
    ):
        check(name, [u"string"])
        check(interaction, [u"string"])
        check(value, [u"stringable", None])
        check(target, [u"string", None])
        self.content_tracking = {
            u"name": name,
            u"value": value,
            u"target": target,
            u"interaction": interaction
        }
        return True

    def get_visitor_id(self):
        u"""
        If the user initiating the request has the Piwik first party cookie,
        this function will try and return the ID parsed from this first party
        cookie.

        If you call this function from a server, where the call is triggered by
        a cron or script not initiated by the actual visitor being tracked,
        then it will return the random Visitor ID that was assigned to this
        visit object.

        This can be used if you wish to record more visits, actions or goals
        for this visitor ID later on.

        :rtype: str
        """
        return self.visitor_id

    def __get_random_string(self, length):
        u"""
        Return a random string

        :param length: Length
        :type length: inte
        :rtype: str
        """
        check(length, [int])
        return (
            u"".join(
                random.choice(
                    string.ascii_uppercase + string.digits
                )
            for _ in range(length)
            )
        )

    def build_random_visitor_id(self):
        u"""
        Return a random visitor ID

        :rtype: str
        """
        return self.__get_random_string(self.LENGTH_VISITOR_ID)

    def set_page_titles(self, page_titles):
        u"""
        Track a page view, return the request body

        :param document_title: The title of the page the user is on
        :type document_title: str
        :rtype: str
        """
        check(page_titles, [list])
        self.page_titles = page_titles
        return True

    def execute(self):
        url = self._get_request()
        return self._send_request(url)

    def set_track_event(self, category, action, name=None, value=None):
        check(category, [u"string"])
        check(action, [u"string"])
        check(name, [u"string", None])
        check(value, [int, None])
        self.event_tracking = {
            u"category": category,
            u"action": action,
            u"name": name,
            u"value": value
        }
        return True

    def set_track_action(self, action_url, action_type):
        u"""
        Track a download or outlink

        :param action_url: URL of the download or outlink
        :type action_url: str
        :param action_type: Type of the action, either "download" or "link"
        :type action_type: str
        :raises: InvalidParameter if action type is unknown
        :rtype: str
        """
        check(action_type, [u"string"])
        check(action_url, [u"string"])
        if action_type not in [u"download", u"link"]:
            raise InvalidParameter(u"Illegal action parameter %s" % action_type)
        self.action_tracking = {
            "type": action_type,
            "url": action_url
        }
        return True

    def set_track_search(self, search, category=None, count=None):
        """
        Track a Site Search query.

        param search: Search query
        :type search: str
        :param search_cat: optional search category
        :type search_cat: str
        :param search_count: umber of search results displayed in the page. If
        search_count=0, the request will appear in "No Result Search Keyword"
        :type search_count: int
        :rtype: None
        """
        check(search, [u"string"])
        check(category, [u"string", None])
        check(count, [int, None])
        self.search_tracking = {}
        self.search_tracking["query"] = search
        if category is not None:
            self.search_tracking["category"] = category
        if count is not None:
            self.search_tracking["count"] = count
        return True

    def _send_request(self, query_vars):
        """
        Make the tracking API request, return the request body

        :param url: TODO
        :type url: str
        :raises: ConfigurationError if the API URL was not set
        :rtype: str
        """
        check(query_vars, [dict])
        if self.api_url is None:
            raise ConfigurationError(u"API URL not set")
        req_headers = {}
        req_cookies = {}
        if self.user_agent is not None:
            req_headers[u"User-Agent"] = self.user_agent
        if self.accept_language is not None:
            req_headers[u"Accept-Language"] = self.accept_language
        if (
                self.request_cookies is not None and
                len(self.request_cookies) > 0
        ):
            req_cookies = self.request_cookies
        req = (
            requests.Request(
                method=u"GET",
                url=self.api_url,
                headers=req_headers,
                cookies=req_cookies,
                params=query_vars
            )
        )
        sess = requests.Session()
        if not self.ssl_verify:
            ##
            ## See: https://stackoverflow.com/a/28002687
            ##
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            sess.verify = False
        prep = sess.prepare_request(req)
        response = sess.send(prep)
        ok = response.status_code in [200, 204]
        err = (not ok)
        ret = {
            u"body_bytes": response.content,
            u"body_str": response.text,
            u"status": response.status_code,
            u"ok": ok,
            u"error": err
        }
        return ret

    def set_ssl_verify(self, verify):
        check(verify, [bool])
        self.ssl_verify = verify
        return True

    def set_custom_variable(self, _id, name, value, scope=u"visit"):
        u"""
        Set a custom variable

        See http://piwik.org/docs/custom-variables/

        :param id: Custom variable slot ID, 1-5
        :type id: int
        :param name: Variable name
        :type name: str
        :param value: Variable value
        :type value: str
        :param scope: Variable scope, either visit or page,
            defaults to visit
        :type scope: str or None
        :rtype: bool
        """
        check(_id, [int])
        check(name, [u"string"])
        check(value, [u"jsonable"])
        check(scope, [u"string"])
        if scope == u"page":
            if self.page_custom_var is None:
                self.page_custom_var = {}
            self.page_custom_var[_id] = (name, value)
        elif scope == u"event":
            if self.event_custom_var is None:
                self.event_custom_var = {}
            self.event_custom_var[_id] = (name, value)
        elif scope == u"visit":
            if self.visitor_custom_var is None:
                self.visitor_custom_var = {}
            self.visitor_custom_var[_id] = (name, value)
        else:
            raise InvalidParameter(u"Invalid scope parameter value %s" % scope)
        return True

    def set_dimension(self, name, value):
        u"""
        Set a custom dimension

        See http://piwik.org/docs/custom-dimensions/

        :param name: Variable name
        :type name: str
        :param value: Variable value
        :type value: str
        :rtype: None
        """
        check(name, [int])
        check(value, [u"stringable"])
        if self.dimensions is None:
            self.dimensions = {}
        self.dimensions[name] = value
        return True

    def set_plugins(self, plugins):
        u"""
        Set supported plugins

        >>> piwiktrackerinstance.set_plugins(flash=True)

        See KNOWN_PLUGINS keys for valid values.

        :param kwargs: A plugin: version dict, e.g. {"java": 6}, see also
            KNOWN_PLUGINS
        :type kwargs: dict of {str: int}
        :rtype: bool
        """
        check(plugins, [dict])
        for plugin, version in plugins.items():
            if plugin not in list(self.KNOWN_PLUGINS.keys()):
                raise ConfigurationError(
                    u"Unknown plugin %s, please use one "
                    u"of %s" %
                    (plugin, list(self.KNOWN_PLUGINS.keys()))
                )
            self.plugins[self.KNOWN_PLUGINS[plugin]] = int(version)
        return True

    def get_custom_variable(self, _id, scope):
        u"""
        Returns the current custom variable stored in a first party cookie.

        :param id: Custom variable slot ID, 1-5
        :type id: int
        :param scope: Variable scope, either visit or page
        :type scope: str
        :rtype: mixed stuff TODO
        """
        check(_id, [int])
        check(scope, [u"string"])
        var_map = None
        if scope == u"visit":
            var_map = self.visitor_custom_var
        elif scope == u"event":
            var_map = self.event_custom_var
        elif scope == u"page":
            var_map = self.page_custom_var
        else:
            raise InvalidParameter(
                u"Bad scope: %s" % scope
            )
        if id not in var_map:
            return None
        return var_map[_id]

    def set_track_ecommerce(
            self,
            _id=None,
            grand_total=None,
            sub_total=None,
            tax=None,
            shipping=None,
            discount=None,
            track_datetime=None,
            items=None
    ):
        check(_id, [int, None])
        check(grand_total, [Decimal, None])
        check(sub_total, [Decimal, None])
        check(tax, [Decimal, None])
        check(shipping, [Decimal, None])
        check(discount, [Decimal, None])
        check(track_datetime, [datetime.datetime, None])
        check(items, [list, None])
        check(scope, [u"string", None])
        self.goal = {}
        self.goal[u"id"] = 0
        if grand_total is not None:
            self.goal[u"revenue"] = grand_total
        self.ecomm_order = {}
        if _id is not None:
            self.ecomm_order[u"id"] = _id
        if sub_total is not None:
            self.ecomm_order[u"sub_total"] = sub_total
        if tax is not None:
            self.ecomm_order[u"tax"] = tax
        if shipping is not None:
            self.ecomm_order[u"shipping"] = shipping
        if discount is not None:
            self.ecomm_order[u"discount"] = discount
        if track_datetime is not None:
            self.ecomm_order[u"track_datetime"] = track_datetime
        if items is not None:
            self.ecomm_order[u"items"] = []
            for item in items:
                if (
                        u"sku" not in item or
                        u"name" not in item or
                        u"category" not in item or
                        u"price" not in item or
                        u"quantity" not in item
                ):
                    raise InvalidParameter(u"Bad item spec: %s" % item)
                self.ecomm_order.append(item)
        return True

    def set_track_goal(self, goal_id, revenue=None):
        u"""
        Record a goal conversion

        :param id_goal: Goal ID
        :type id_goal: int
        :param revenue: Revenue for this conversion
        :type revenue: int (TODO why int here and not float!?)
        :rtype: str
        """
        check(goal_id, [int])
        check(revenue, [Decimal, None])
        self.goal = {
            "id": goal_id,
            "revenue": revenue
        }
        return True

    def set_ecommerce_view(
            self,
            sku=None,
            name=None,
            category=None,
            price=None
    ):
        u"""
        Set the page view as an item/product page view, or an ecommerce
        category page view.

        This method will set three custom variables of "page" scope with the
        SKU, name and category for this page view.

        On a category page you may set the category argument only.

        Tracking product/category page views will allow Piwik to report on
        product and category conversion rates.

        To enable ecommerce tracking see doc/install.rst

        :param SKU: Product SKU being viewed
        :type SKU: str or None
        :param name: Name of the product
        :type name: str or None
        :param category: Name of the category for the current
            category page or the product
        :type category: str, list or None
        :param price: Price of the product
        :type price: float or None
        :rtype: bool
        """
        check(sku, [u"string", None])
        check(name, [u"string", None])
        check(category, [u"string", None])
        check(price, [Decimal, None])
        if category is not None:
            self.page_custom_var[5] = (u"_pkc", category)
        if sku is not None:
            self.page_custom_var[3] = (u"_pks", sku)
        if price is not None:
            self.page_custom_var[2] = (u"_pkp", price)
        if name is not None:
            self.page_custom_var[4] = (u"_pkn", name)
        return True
