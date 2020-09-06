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
from ansible_collections.steampunk.unit.plugins.modules import listener


class TestValidateCurrentState:
    def test_missing_pass(self, mocker):
        validate_pass = mocker.patch.object(validation, "validate_pass")
        validate_pass.return_value = ["bad bad error"]

        client = mocker.Mock()

        with pytest.raises(errors.UnitError, match="bad bad error"):
            listener.validate_current_state(
                client, {"pass": "some/destination"},
            )

        client.get.assert_not_called()

    def test_missing_cert(self, mocker):
        validate_pass = mocker.patch.object(validation, "validate_pass")
        validate_pass.return_value = []

        client = mocker.Mock()
        client.get.return_value = {}

        with pytest.raises(errors.UnitError, match="bundle_name"):
            listener.validate_current_state(client, {
                "pass": "some/destination",
                "tls": {"certificate": "bundle_name"},
            })

        client.get.assert_called_once_with(("certificates", "bundle_name"))

    def test_all_ok(self, mocker):
        validate_pass = mocker.patch.object(validation, "validate_pass")
        validate_pass.return_value = []

        client = mocker.Mock()
        client.get.return_value = dict(a=3)

        listener.validate_current_state(client, {
            "pass": "some/destination",
            "tls": {"certificate": "bundle_name"},
        })

        client.get.assert_called_once_with(("certificates", "bundle_name"))


class TestMain:
    @pytest.mark.parametrize("state", ["present", "absent"])
    def test_pattern_required(self, mocker, ansible_run, state):
        run_mock = mocker.patch.object(listener, "run")

        ansible_run.run(listener, **{"pass": "routes/x", "state": state})

        assert ansible_run.success is False
        assert "pattern" in ansible_run.result["msg"]
        run_mock.assert_not_called()

    def test_pass_required_when_state_present(self, mocker, ansible_run):
        run_mock = mocker.patch.object(listener, "run")

        ansible_run.run(listener, pattern="sample")

        assert ansible_run.success is False
        assert "pass" in ansible_run.result["msg"]
        run_mock.assert_not_called()

    def test_minimal_params_state_present(self, mocker, ansible_run):
        run_mock = mocker.patch.object(listener, "run")
        run_mock.return_value = dict(k="v")

        ansible_run.run(listener, **{"pattern": "sample", "pass": "dest"})

        assert ansible_run.success is True
        assert ansible_run.result == dict(k="v")
        run_mock.assert_called_with({
            "pattern": "sample",
            "pass": "dest",
            "state": "present",
            "provider": {
                "verify": True,
                "ca_path": None,
                "endpoint": None,
                "password": None,
                "username": None,
            },
            "tls": None,
        }, False)

    def test_minimal_params_state_absent(self, mocker, ansible_run):
        run_mock = mocker.patch.object(listener, "run")
        run_mock.return_value = dict(k="v")

        ansible_run.run(listener, pattern="sample", state="absent")

        assert ansible_run.success is True
        assert ansible_run.result == dict(k="v")
        run_mock.assert_called_with({
            "pattern": "sample",
            "pass": None,
            "state": "absent",
            "provider": {
                "verify": True,
                "ca_path": None,
                "endpoint": None,
                "password": None,
                "username": None,
            },
            "tls": None,
        }, False)

    def test_full_params(self, mocker, ansible_run):
        run_mock = mocker.patch.object(listener, "run")
        run_mock.return_value = dict(k="v")

        ansible_run.run(listener, **{
            "pattern": "sample",
            "pass": "dest",
            "state": "present",
            "provider": {
                "verify": True,
                "ca_path": "ca_path",
                "endpoint": "unix:///path",
                "password": "pass",
                "username": "user",
            },
            "tls": {
                "certificate": "bundle",
            },
        })

        assert ansible_run.success is True
        assert ansible_run.result == dict(k="v")
        run_mock.assert_called_with({
            "pattern": "sample",
            "pass": "dest",
            "state": "present",
            "provider": {
                "verify": True,
                "ca_path": "ca_path",
                "endpoint": "unix:///path",
                "password": "pass",
                "username": "user",
            },
            "tls": {
                "certificate": "bundle",
            },
        }, False)
