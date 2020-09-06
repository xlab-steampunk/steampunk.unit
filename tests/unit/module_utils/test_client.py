# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError

from ansible_collections.steampunk.unit.plugins.module_utils import (
    client, errors,
)


class TestResponseInit:
    def test_with_valid_json(self):
        resp = client.Response(201, '{"some": ["json", "data", 3]}')

        assert 201 == resp.status
        assert '{"some": ["json", "data", 3]}' == resp.data
        assert {"some": ["json", "data", 3]} == resp.json

    def test_with_invalid_json(self):
        resp = client.Response(404, "")

        assert 404 == resp.status
        assert "" == resp.data
        with pytest.raises(errors.UnitError, match="invalid json"):
            resp.json


class TestClientInit:
    @pytest.mark.parametrize("prefix", [
        "invalid://",  # invalid string
        "http:/",  # missiing one / at the end
        "https//",  # missing :
        "unix://",  # missing / at the end (socket paths should be absolute)
    ])
    def test_invalid_prefix(self, mocker, prefix):
        mocker.patch.object(client, "Request")

        with pytest.raises(errors.UnitError, match="start with"):
            client.Client(prefix + "some/path", None, None, False, None)

    def test_unix_socket_parse(self, mocker):
        request = mocker.patch.object(client, "Request")

        client.Client("unix:///var/run/sock", "u", "p", True, "ca")

        request.assert_called_once_with(unix_socket="/var/run/sock")

    @pytest.mark.parametrize("prefix", ["http", "https"])
    def test_ip_socket_parse(self, mocker, prefix):
        request = mocker.patch.object(client, "Request")

        client.Client(prefix + "://domain.name", "u", "p", True, "ca")

        request.assert_called_once_with(
            url_username="u", url_password="p", force_basic_auth=True,
            validate_certs=True, ca_path="ca",
        )


class TestClientRequest:
    def test_ok_using_unix_socket_no_data(self, mocker):
        request = mocker.patch.object(client, "Request").return_value
        request.open.return_value.getcode.return_value = 200
        request.open.return_value.read.return_value = '{"k": "v"}'
        c = client.Client("unix:///path", "u", "p", True, "ca")

        r = c.request("GET", ("config", "routes"))

        request.open.assert_called_once_with(
            method="GET", url="http://localhost/config/routes", data=None,
        )
        assert r.status == 200
        assert r.json == dict(k="v")

    def test_ok_using_unix_socket_with_data(self, mocker):
        request = mocker.patch.object(client, "Request").return_value
        request.open.return_value.getcode.return_value = 404
        request.open.return_value.read.return_value = '{"k": "v"}'
        c = client.Client("unix:///path", "u", "p", True, "ca")

        r = c.request("PUT", ("config", "listeners"), dict(my="data"))

        request.open.assert_called_once_with(
            method="PUT", url="http://localhost/config/listeners",
            data='{"my":"data"}',
        )
        assert r.status == 404
        assert r.json == dict(k="v")

    def test_ok_using_ip_socket_no_data(self, mocker):
        request = mocker.patch.object(client, "Request").return_value
        request.open.return_value.getcode.return_value = 200
        request.open.return_value.read.return_value = '{"k": "v"}'
        c = client.Client("http://host/", "u", "p", True, "ca")

        r = c.request("GET", ("config", "routes"))

        request.open.assert_called_once_with(
            method="GET", url="http://host/config/routes", data=None,
        )
        assert r.status == 200
        assert r.json == dict(k="v")

    def test_ok_using_ip_socket_with_data(self, mocker):
        request = mocker.patch.object(client, "Request").return_value
        request.open.return_value.getcode.return_value = 404
        request.open.return_value.read.return_value = '{"k": "v"}'
        c = client.Client("https://host", "u", "p", True, "ca")

        r = c.request("PUT", ("config", "applications"), dict(number=4))

        request.open.assert_called_once_with(
            method="PUT", url="https://host/config/applications",
            data='{"number":4}',
        )
        assert r.status == 404
        assert r.json == dict(k="v")

    def test_path_escaping(self, mocker):
        request = mocker.patch.object(client, "Request").return_value
        request.open.return_value.getcode.return_value = 200
        request.open.return_value.read.return_value = ""
        c = client.Client("https://host", "u", "p", True, "ca")

        c.request("PUT", ("config", "a/b"))

        request.open.assert_called_once_with(
            method="PUT", url="https://host/config/a%2Fb", data=None,
        )

    def test_empty_path(self, mocker):
        request = mocker.patch.object(client, "Request").return_value
        request.open.return_value.getcode.return_value = 200
        request.open.return_value.read.return_value = ""
        c = client.Client("https://host", "u", "p", True, "ca")

        c.request("PUT", ())

        request.open.assert_called_once_with(
            method="PUT", url="https://host", data=None,
        )

    def test_http_error_handling(self, mocker):
        request = mocker.patch.object(client, "Request").return_value
        request.open.side_effect = HTTPError("url", 404, "missing", {}, None)
        c = client.Client("https://host", "u", "p", True, "ca")

        r = c.request("PUT", ("config", "a/b"))

        assert r.status == 404
        assert r.data == "missing"

    def test_url_error_handling(self, mocker):
        request = mocker.patch.object(client, "Request").return_value
        request.open.side_effect = URLError("bad error")
        c = client.Client("https://host", "u", "p", True, "ca")

        with pytest.raises(errors.UnitError, match="request failed"):
            c.request("get", ("config", "c"))


class TestClientGet:
    def test_ok(self, mocker):
        c = client.Client("https://host", "u", "p", True, "ca")
        request = mocker.patch.object(c, "request")
        request.return_value = client.Response(200, '{"k":"v"}')

        obj = c.get(("a", "b"))

        request.assert_called_once_with("GET", ("a", "b"))
        assert obj == dict(k="v")

    def test_missing(self, mocker):
        c = client.Client("https://host", "u", "p", True, "ca")
        request = mocker.patch.object(c, "request")
        request.return_value = client.Response(404, "")

        obj = c.get(("a", "b"))

        request.assert_called_once_with("GET", ("a", "b"))
        assert obj == {}

    def test_failure(self, mocker):
        c = client.Client("https://host", "u", "p", True, "ca")
        request = mocker.patch.object(c, "request")
        request.return_value = client.Response(403, "")

        with pytest.raises(errors.UnitError, match="403"):
            c.get(("a", "b"))

        request.assert_called_once_with("GET", ("a", "b"))


class TestClientPut:
    def test_ok_on_first_try(self, mocker):
        c = client.Client("https://host", "u", "p", True, "ca")
        request = mocker.patch.object(c, "request")
        request.side_effect = (
            client.Response(200, '{"k":"v"}'),
            Exception("Should not reach this"),
        )

        c.put(("a", "b"), dict(my=5))

        request.assert_called_once_with("PUT", ("a", "b"), dict(my=5))

    def test_ok_on_third_retry(self, mocker):
        c = client.Client("https://host", "u", "p", True, "ca")
        request = mocker.patch.object(c, "request")
        request.side_effect = (
            client.Response(404, ""),
            client.Response(404, ""),
            client.Response(200, '{"k":"v"}'),
            Exception("Should not reach this"),
        )

        c.put(("a", "b", "c"), dict(my=5))

        assert request.call_count == 3
        request.assert_has_calls((
            mocker.call("PUT", ("a", "b", "c"), dict(my=5)),
            mocker.call("PUT", ("a", "b"), dict(c=dict(my=5))),
            mocker.call("PUT", ("a", ), dict(b=dict(c=dict(my=5)))),
        ))

    def test_run_out_of_path_segments(self, mocker):
        c = client.Client("https://host", "u", "p", True, "ca")
        request = mocker.patch.object(c, "request")
        request.side_effect = (
            client.Response(404, ""),
            client.Response(404, ""),
            Exception("Should not reach this"),
        )

        with pytest.raises(errors.UnitError, match="bug"):
            c.put(("a", ), dict(my=5))

        assert request.call_count == 2

    def test_error_during_retry(self, mocker):
        c = client.Client("https://host", "u", "p", True, "ca")
        request = mocker.patch.object(c, "request")
        request.side_effect = (
            client.Response(404, ""),
            client.Response(403, ""),
            Exception("Should not reach this"),
        )

        with pytest.raises(errors.UnitError, match="403"):
            c.put(("a", "b"), dict(my=5))

        assert request.call_count == 2


class TestClientDelete:
    def test_ok(self, mocker):
        c = client.Client("https://host", "u", "p", True, "ca")
        request = mocker.patch.object(c, "request")
        request.return_value = client.Response(200, "")

        c.delete(("a", "b"))

        request.assert_called_once_with("DELETE", ("a", "b"))

    def test_error(self, mocker):
        c = client.Client("https://host", "u", "p", True, "ca")
        request = mocker.patch.object(c, "request")
        request.return_value = client.Response(400, "")

        with pytest.raises(errors.UnitError, match="400"):
            c.delete(("a", "b"))

        request.assert_called_once_with("DELETE", ("a", "b"))


class TestGetClient:
    def test_no_endpoint_first_default(self, mocker):
        cmock = mocker.patch.object(client, "Client")

        client.get_client(dict(
            endpoint=None,
            username=None,
            password=None,
            verify=True,
            ca_path=None,
        ))

        cmock.assert_called_once_with(
            "unix:///var/run/unit/control.sock", username=None, password=None,
            verify=True, ca_path=None,
        )

    def test_no_endpoint_second_default(self, mocker):
        c1 = mocker.Mock()
        c1.get.side_effect = errors.UnitError("Fail")
        c2 = mocker.Mock()
        cmock = mocker.patch.object(client, "Client")
        cmock.side_effect = (c1, c2)

        client.get_client(dict(
            endpoint=None,
            username=None,
            password=None,
            verify=False,
            ca_path="ca_path",
        ))

        assert cmock.call_count == 2
        cmock.assert_has_calls((
            mocker.call(
                "unix:///var/run/unit/control.sock", username=None,
                password=None, verify=False, ca_path="ca_path",
            ),
            mocker.call(
                "unix:///var/run/control.unit.sock", username=None,
                password=None, verify=False, ca_path="ca_path",
            ),
        ))

    def test_no_endpoint_none_of_defauls(self, mocker):
        c1 = mocker.Mock()
        c1.get.side_effect = errors.UnitError("Fail1")
        c2 = mocker.Mock()
        c2.get.side_effect = errors.UnitError("Fail2")
        cmock = mocker.patch.object(client, "Client")
        cmock.side_effect = (c1, c2)

        with pytest.raises(errors.UnitError, match="valid endpoints"):
            client.get_client(dict(
                endpoint=None,
                username=None,
                password="pass",
                verify=False,
                ca_path=None,
            ))

        assert cmock.call_count == 2
        cmock.assert_has_calls((
            mocker.call(
                "unix:///var/run/unit/control.sock", username=None,
                password="pass", verify=False, ca_path=None,
            ),
            mocker.call(
                "unix:///var/run/control.unit.sock", username=None,
                password="pass", verify=False, ca_path=None,
            ),
        ))

    def test_endpoint_ok(self, mocker):
        cmock = mocker.patch.object(client, "Client")

        client.get_client(dict(
            endpoint="unix:///var/sock.path",
            username="user",
            password=None,
            verify=True,
            ca_path=None,
        ))

        cmock.assert_called_once_with(
            "unix:///var/sock.path", username="user", password=None,
            verify=True, ca_path=None,
        )

    def test_endpoint_fail(self, mocker):
        c1 = mocker.Mock()
        c1.get.side_effect = errors.UnitError("Fail1")
        cmock = mocker.patch.object(client, "Client")
        cmock.side_effect = (c1, )

        with pytest.raises(errors.UnitError, match="valid endpoints"):
            client.get_client(dict(
                endpoint="unix:///var/sock.path",
                username=None,
                password=None,
                verify=False,
                ca_path=None,
            ))

        cmock.called_once_with(
            "unix:///var/sock.path", username=None, password=None,
            verify=False, ca_path=None,
        )
