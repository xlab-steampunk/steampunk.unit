# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from ansible_collections.steampunk.unit.plugins.module_utils import (
    validation, errors,
)


class TestReportError:
    def test_report_no_error(self):
        validation.report_error([])

    def test_report_errors(self):
        with pytest.raises(errors.UnitError, match="my error"):
            validation.report_error(["This is my error"])


class TestValidatePass:
    def test_missing_destination(self, mocker):
        client = mocker.Mock()
        client.get.return_value = {}

        msgs = validation.validate_pass(client, "applications/test")

        assert len(msgs) == 1
        assert "does not exist" in msgs[0]

    def test_missing_php_target(self, mocker):
        client = mocker.Mock()
        client.get.return_value = dict(a=1)

        msgs = validation.validate_pass(client, "applications/test/target")

        assert len(msgs) == 1
        assert "PHP" in msgs[0]

    def test_ok_destination(self, mocker):
        client = mocker.Mock()
        client.get.return_value = dict(a=1)

        msgs = validation.validate_pass(client, "applications/test")

        assert msgs == []

    def test_ok_php_target(self, mocker):
        client = mocker.Mock()
        client.get.return_value = dict(targets=dict(dest={}))

        msgs = validation.validate_pass(client, "applications/test/dest")

        assert msgs == []
