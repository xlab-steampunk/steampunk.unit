# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.steampunk.unit.plugins.module_utils import utils


class TestResultInit:
    def test_no_change(self):
        data = dict(a=1, b="c")

        r = utils.Result(data, data)

        assert r.changed is False
        assert dict(
            changed=False, diff=dict(before=data, after=data), object=data,
        ) == dict(r)

    def test_change(self):
        current = dict(a=1, b="c")
        desired = dict(a=2, d="e")

        r = utils.Result(current, desired)

        assert r.changed is True
        assert dict(
            changed=True,
            diff=dict(before=current, after=desired),
            object=desired,
        ) == dict(r)


class TestResultAddObjectFields:
    def test_add_change(self):
        r = utils.Result({}, dict(a=1, b="c"))

        r.add_object_fields(a=2, d="e")

        assert dict(a=2, b="c", d="e") == r["object"]


class TestCreate:
    def test_check_mode_no_change(self, mocker):
        client = mocker.Mock()
        client.get.return_value = dict(a=1)

        r = utils.create(client, (), dict(a=1), True)

        client.get.assert_called_once_with(())
        client.put.assert_not_called()
        assert dict(
            changed=False,
            diff=dict(before=dict(a=1), after=dict(a=1)),
            object=dict(a=1),
        ) == dict(r)

    def test_check_mode_change(self, mocker):
        client = mocker.Mock()
        client.get.return_value = dict(a=1)

        r = utils.create(client, (), dict(a=2), True)

        client.get.assert_called_once_with(())
        client.put.assert_not_called()
        assert dict(
            changed=True,
            diff=dict(before=dict(a=1), after=dict(a=2)),
            object=dict(a=2),
        ) == dict(r)

    def test_no_change(self, mocker):
        client = mocker.Mock()
        client.get.return_value = dict(a=1)

        r = utils.create(client, (), dict(a=1), False)

        client.get.assert_called_once_with(())
        client.put.assert_not_called()
        assert dict(
            changed=False,
            diff=dict(before=dict(a=1), after=dict(a=1)),
            object=dict(a=1),
        ) == dict(r)

    def test_change(self, mocker):
        client = mocker.Mock()
        client.get.return_value = dict(a=1)

        r = utils.create(client, (), dict(a=2), False)

        client.get.assert_called_once_with(())
        client.put.assert_called_once_with((), dict(a=2))
        assert dict(
            changed=True,
            diff=dict(before=dict(a=1), after=dict(a=2)),
            object=dict(a=2),
        ) == dict(r)


class TestDelete:
    def test_check_mode_no_change(self, mocker):
        client = mocker.Mock()
        client.get.return_value = {}

        r = utils.delete(client, (), True)

        client.get.assert_called_once_with(())
        client.delete.assert_not_called()
        assert dict(
            changed=False,
            diff=dict(before={}, after={}),
            object={},
        ) == dict(r)

    def test_check_mode_change(self, mocker):
        client = mocker.Mock()
        client.get.return_value = dict(a=1)

        r = utils.delete(client, (), True)

        client.get.assert_called_once_with(())
        client.delete.assert_not_called()
        assert dict(
            changed=True,
            diff=dict(before=dict(a=1), after={}),
            object={},
        ) == dict(r)

    def test_no_change(self, mocker):
        client = mocker.Mock()
        client.get.return_value = {}

        r = utils.delete(client, (), False)

        client.get.assert_called_once_with(())
        client.delete.assert_not_called()
        assert dict(
            changed=False,
            diff=dict(before={}, after={}),
            object={},
        ) == dict(r)

    def test_change(self, mocker):
        client = mocker.Mock()
        client.get.return_value = dict(a=1)

        r = utils.delete(client, (), False)

        client.get.assert_called_once_with(())
        client.delete.assert_called_once_with(())
        assert dict(
            changed=True,
            diff=dict(before=dict(a=1), after={}),
            object={},
        ) == dict(r)


class TestFilterDict:
    def test_filter(self):
        assert dict(a=1, b="c") == utils.filter_dict(
            dict(a=1, b="c", d="e", f=None), "a", "b",
        )


class TestCompactDict:
    def test_compact(self):
        assert dict(
            a=1, b="c", d="e", g=[], h={}, x=0,
        ) == utils.compact_dict(dict(
            a=1, b="c", d="e", f=None, g=[], h={}, x=0,
        ))
