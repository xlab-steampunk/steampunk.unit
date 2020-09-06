# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes


class AnsibleRunEnd(Exception):
    """ Termination signal """


class AnsibleRun:
    def __init__(self):
        self.success = None
        self.result = None

    def run(self, module, **args):
        a = dict(
            _ansible_remote_tmp="/tmp",
            _ansible_keep_remote_files=False,
        )
        a.update(args)
        basic._ANSIBLE_ARGS = to_bytes(json.dumps(dict(ANSIBLE_MODULE_ARGS=a)))
        try:
            module.main()
        except AnsibleRunEnd:
            # This is what we expect
            return
        assert False, "Module is not calling exit_json or fail_json."

    def exit_json(self, **result):
        self.success = True
        self.result = result
        raise AnsibleRunEnd()

    def fail_json(self, **result):
        self.success = False
        self.result = result
        self.result["changed"] = result.get("changed", False)
        raise AnsibleRunEnd()


@pytest.fixture
def ansible_run(mocker):
    ansible_run = AnsibleRun()
    mocker.patch.multiple(
        basic.AnsibleModule,
        exit_json=ansible_run.exit_json,
        fail_json=ansible_run.fail_json,
    )
    return ansible_run
