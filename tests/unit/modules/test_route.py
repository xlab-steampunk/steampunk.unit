# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from ansible_collections.steampunk.unit.plugins.module_utils import (
    errors, validation,
)
from ansible_collections.steampunk.unit.plugins.modules import route


class TestValidateAction:
    def test_pass_validation(self, mocker):
        validate_pass = mocker.patch.object(validation, "validate_pass")
        validate_pass.return_value = []

        msgs = route.validate_action(None, {"pass": "applications/sample"})

        validate_pass.assert_called_once_with(None, "applications/sample")
        assert msgs == []

    def test_fallback_validation(self, mocker):
        validate_pass = mocker.patch.object(validation, "validate_pass")
        validate_pass.side_effect = [[0], [1], [2]]

        msgs = route.validate_action(None, {
            "pass": "applications/sample",
            "fallback": {
                "pass": "aplications/admin",
                "fallback": {
                    "share": "/tmp",
                },
            },
        })

        assert validate_pass.call_count == 2
        assert msgs == [0, 1]

    def test_nothing_to_validate(self, mocker):
        validate_pass = mocker.patch.object(validation, "validate_pass")

        msgs = route.validate_action(None, {"share": "/tmp/www"})

        validate_pass.assert_not_called()
        assert msgs == []


class TestValidateCurrentState:
    def test_missing_action(self, mocker):
        validate_action = mocker.patch.object(route, "validate_action")

        with pytest.raises(errors.UnitError, match="step 0"):
            route.validate_current_state(None, [{}])

        validate_action.assert_not_called()

    def test_action_present(self, mocker):
        validate_action = mocker.patch.object(route, "validate_action")
        validate_action.return_value = []

        route.validate_current_state(None, [
            dict(match=dict(method="GET"), action=dict(share="/tmp/read")),
            dict(action=dict(share="/tmp/other")),
        ])

        assert validate_action.call_count == 2


class TestBuildPayload:
    def test_conversion(self):
        assert [
            {
                "match": {"uri": "/something/*"},
                "action": {"pass": "applications/demo"},
            },
            {
                "action": {"share": "/tmp"},
            },
        ] == route.build_payload([
            {
                "match": {
                    "method": None,
                    "arguments": None,
                    "cookies": None,
                    "destination": None,
                    "headers": None,
                    "host": None,
                    "scheme": None,
                    "source": None,
                    "uri": "/something/*",
                },
                "action": {
                    "return": None,
                    "fallback": None,
                    "location": None,
                    "pass": "applications/demo",
                    "proxy": None,
                    "share": None,
                },
            },
            {
                "match": None,
                "action": {
                    "share": "/tmp",
                    "fallback": None,
                    "location": None,
                    "pass": None,
                    "proxy": None,
                    "return": None,
                },
            },
        ])


class TestMain:
    def test_name_required_if_global_is_false(self, mocker, ansible_run):
        run_mock = mocker.patch.object(route, "run")

        ansible_run.run(route, steps=[])

        assert ansible_run.success is False
        assert "name" in ansible_run.result["msg"]
        run_mock.assert_not_called()

    def test_steps_required_if_state_present(self, mocker, ansible_run):
        run_mock = mocker.patch.object(route, "run")

        ansible_run.run(route, name="sample")

        assert ansible_run.success is False
        assert "steps" in ansible_run.result["msg"]
        run_mock.assert_not_called()

    def test_steps_required_if_state_present_global(self, mocker, ansible_run):
        run_mock = mocker.patch.object(route, "run")

        ansible_run.run(route, **{"global": True})

        assert ansible_run.success is False
        assert "steps" in ansible_run.result["msg"]
        run_mock.assert_not_called()

    def test_minimal_params_with_name(self, mocker, ansible_run):
        run_mock = mocker.patch.object(route, "run")
        run_mock.return_value = dict(k="v")

        ansible_run.run(route, name="sample", steps=[])

        assert ansible_run.success is True
        assert ansible_run.result == dict(k="v")
        run_mock.assert_called_with({
            "name": "sample",
            "steps": [],
            "global": False,
            "state": "present",
            "provider": {
                "verify": True,
                "ca_path": None,
                "endpoint": None,
                "password": None,
                "username": None,
            },
        }, False)

    def test_minimal_params_with_global(self, mocker, ansible_run):
        run_mock = mocker.patch.object(route, "run")
        run_mock.return_value = dict(k="v")

        ansible_run.run(route, **{"global": True, "steps": []})

        assert ansible_run.success is True
        assert ansible_run.result == dict(k="v")
        run_mock.assert_called_with({
            "name": None,
            "steps": [],
            "global": True,
            "state": "present",
            "provider": {
                "verify": True,
                "ca_path": None,
                "endpoint": None,
                "password": None,
                "username": None,
            },
        }, False)

    def test_minimal_params_state_absent(self, mocker, ansible_run):
        run_mock = mocker.patch.object(route, "run")
        run_mock.return_value = dict(k="v")

        ansible_run.run(route, state="absent", name="sample")

        assert ansible_run.success is True
        assert ansible_run.result == dict(k="v")
        run_mock.assert_called_with({
            "name": "sample",
            "steps": None,
            "global": False,
            "state": "absent",
            "provider": {
                "verify": True,
                "ca_path": None,
                "endpoint": None,
                "password": None,
                "username": None,
            },
        }, False)

    def test_minimal_params_state_absent_global(self, mocker, ansible_run):
        run_mock = mocker.patch.object(route, "run")
        run_mock.return_value = dict(k="v")

        ansible_run.run(route, **{"state": "absent", "global": True})

        assert ansible_run.success is True
        assert ansible_run.result == dict(k="v")
        run_mock.assert_called_with({
            "name": None,
            "steps": None,
            "global": True,
            "state": "absent",
            "provider": {
                "verify": True,
                "ca_path": None,
                "endpoint": None,
                "password": None,
                "username": None,
            },
        }, False)

    def test_full_params(self, mocker, ansible_run):
        run_mock = mocker.patch.object(route, "run")
        run_mock.return_value = dict(k="v")

        ansible_run.run(route, **{
            "global": True,
            "name": "sample",
            "provider": {
                "ca_path": "/my/path",
                "endpoint": "unix:///socket",
                "password": "pass",
                "username": "user",
                "verify": False,
            },
            "state": "present",
            "steps": [
                {
                    "match": {
                        "method": ["HEAD", "GET"],
                    },
                    "action": {
                        "return": 302,
                    },
                },
                {
                    "action": {
                        "share": "/tmp",
                    },
                },
            ],
        })

        assert ansible_run.success is True
        assert ansible_run.result == dict(k="v")
        run_mock.assert_called_with({
            "global": True,
            "name": "sample",
            "provider": {
                "ca_path": "/my/path",
                "endpoint": "unix:///socket",
                "password": "pass",
                "username": "user",
                "verify": False,
            },
            "state": "present",
            "steps": [
                {
                    "match": {
                        "method": ["HEAD", "GET"],
                        "arguments": None,
                        "cookies": None,
                        "destination": None,
                        "headers": None,
                        "host": None,
                        "scheme": None,
                        "source": None,
                        "uri": None,
                    },
                    "action": {
                        "return": 302,
                        "fallback": None,
                        "location": None,
                        "pass": None,
                        "proxy": None,
                        "share": None,
                    },
                },
                {
                    "match": None,
                    "action": {
                        "share": "/tmp",
                        "fallback": None,
                        "location": None,
                        "pass": None,
                        "proxy": None,
                        "return": None,
                    },
                },
            ],
        }, False)
