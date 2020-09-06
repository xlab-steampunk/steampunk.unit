# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.module_utils.urls import Request

from .errors import UnitError


class Response:
    def __init__(self, status, data):
        self.status = status
        self.data = data
        self._json = None

    @property
    def json(self):
        if self._json is None:
            try:
                self._json = json.loads(self.data)
            except ValueError:
                raise UnitError(
                    "Unit returned an invalid json: {0}".format(self.data)
                )
        return self._json


class Client:
    VALID_PREFIXES = "http://", "https://", "unix:///"

    def __init__(self, endpoint, username, password, verify, ca_path):
        valid_prefix = any(endpoint.startswith(p) for p in self.VALID_PREFIXES)
        if not valid_prefix:
            raise UnitError(
                "Endpoint should start with one of the following: {0}".format(
                    ", ".join(self.VALID_PREFIXES),
                )
            )

        if endpoint.startswith("unix://"):
            self._client = Request(unix_socket=endpoint[7:])
            self._host = "http://localhost"
        else:
            self._client = Request(
                force_basic_auth=True, validate_certs=verify, ca_path=ca_path,
                url_username=username, url_password=password,
            )
            self._host = endpoint.rstrip("/")

    def request(self, method, path, data=None):
        url = (
            self._host + "/" + "/".join(quote(s, safe="") for s in path)
        ).rstrip("/")

        if data is not None:
            data = json.dumps(data, separators=(",", ":"))

        try:
            raw_resp = self._client.open(method=method, url=url, data=data)
            return Response(raw_resp.getcode(), raw_resp.read())
        except HTTPError as e:
            # This is not an error, since client consumers might be able to
            # work around/expect non 20x codes.
            return Response(e.code, e.reason)
        except URLError as e:
            raise UnitError("{0} request failed: {1}".format(method, e.reason))

    def get(self, path):
        r = self.request("GET", path)
        if r.status == 200:
            return r.json
        if r.status == 404:
            return {}

        raise UnitError(
            "Invalid response: ({0}) - {1}".format(r.status, r.data)
        )

    def put(self, path, data):
        # Any of the parrent sections might be missing at this point, so do
        # not fail on 404. Instead, incrementally build the payload until we
        # get a non-404 response back.
        #
        # Example: If the following request
        #
        #   POST /config/listeners/127.0.0.1:80
        #     {"pass": "applications/test}
        #
        # returns 404, we will retry with the following request:
        #
        #   POST /config/listeners
        #    {"127.0.0.1:80": {"pass": "applications/test}}
        #
        # And if this still fails, we will resort to
        #
        #   POST /config
        #    {"listeners": {"127.0.0.1:80": {"pass": "applications/test}}}
        #
        # All this stops when:
        #
        #  1. we get back a 200 status (success), or
        #  2. we get back invalid status (fail), or
        #  3. when we run out of path segments (fail).

        while True:
            r = self.request("PUT", path, data)
            if r.status == 200:
                # Success, we managed to get our data pushed to the server.
                return

            if r.status != 404:
                # Something bad happened. Stop being smart and bail.
                raise UnitError(
                    "Invalid response: ({0}) - {1}".format(r.status, r.data)
                )

            if not path:
                # We ran out of parent path segments. Bail.
                raise UnitError(
                    "Ran out of parent path segments. This probaly indicates "
                    "a bug in NGINX Unit Ansible Collection or in the NGINX "
                    "Unit itself. Please file an issue in the collection's "
                    "issue tracker. Thank you in advance for providing as "
                    "much relevant data in the issue as possible ;)"
                )

            # Missing parent category. Retry push with expanded data on
            # parent path.
            data = {path[-1]: data}
            path = path[:-1]

    def delete(self, path):
        r = self.request("DELETE", path)
        # Yes, unit returns 200 on DELETE ...
        if r.status != 200:
            raise UnitError(
                "Invalid response: ({0}) - {1}".format(r.status, r.data)
            )


_DEFAULT_ENDPOINTS = (
    "unix:///var/run/unit/control.sock",  # RHEL-like distros
    "unix:///var/run/control.unit.sock",  # Debian-derived distros
)


def get_client(provider):
    # We need to process endpoint a bit differently
    params = dict((k, v) for k, v in provider.items() if k != "endpoint")

    if provider["endpoint"]:
        endpoints = (provider["endpoint"], )
    else:
        endpoints = _DEFAULT_ENDPOINTS

    for endpoint in endpoints:
        client = Client(endpoint, **params)
        try:
            client.get(())
            return client
        except UnitError:
            pass  # Try next available endpoint

    raise UnitError(
        "No valid endpoints found amongst the candidates: {0}".format(
            ", ".join(endpoints),
        )
    )
