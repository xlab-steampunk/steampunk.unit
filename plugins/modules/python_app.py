#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: python_app
author:
  - Tadej Borovšak (@tadeboro)
short_description: Manage NGINX Unit python application
description:
  - Manage NGINX Unit python application configuration.
  - Upstream docs are at U(https://unit.nginx.org/configuration/#python).
extends_documentation_fragment:
  - steampunk.unit.application
  - steampunk.unit.provider
  - steampunk.unit.state
options:

  version:
    description:
      - Version of python module to use.
      - Use this module if you have more than one version of python module
        installed (eg. python 2 and python 3).
      - If this option is not set, unit will use the latest available module.
    type: str

  module:
    description:
      - WSGI module to run.
      - Required if I(state) is C(present).
    type: str

  path:
    description:
      - Additional lookup path for Python modules; this string is inserted
        into C(sys.path).
    type: str

  home:
    description:
      - Virtual environment to use. Absolute, or relative to
        I(working_directory).
    type: path
"""

EXAMPLES = """
- name: Create python 2 application
  steampunk.unit.python_app:
    name: demo
    version: "2"
    no_processes: 10
    working_directory: /www/store/
    path: /www/store/cart/
    callable: app
    home: /www/store/.virtualenv/
    module": wsgi
    user": www
    group": www

- name: Delete application
  steampunk.unit.python_app:
    name: demo
    state: absent
"""

RETURN = """
object:
  description: Object representing NGINX Unit Python application.
  returned: On success and if I(state) == C(present)
  type: dict
  contains:

    name:
      description: Application name.
      returned: always
      type: str

    limits:
      description: Set the application's lifecycle parameters.
      returned: if set
      type: dict
      contains:

        timeout:
          description: Request timeout in seconds.
          type: int

        requests:
          description: Maximum number of requests Unit allows an app to serve.
          type: int

    no_processes:
      returned: if set
      description: Number of processes that should be running at one time.
      type: int

    processes:
      description: Dynamic process limits.
      returned: if set
      type: dict
      contains:

        max:
          description: Maximum number of application processes.
          type: int

        spare:
          description: Minimum number of idle processes.
          type: int

        idle_timeout:
          description: Time in seconds before terminating an idle process.
          type: int

    working_directory:
      description: The app's working directory.
      returned: if set
      type: str

    user:
      description: Username that runs the app process.
      returned: if set
      type: str

    group:
      description: Group name that runs the app process.
      returned: if set
      type: str

    environment:
      description: Environment variables to be passed to the application.
      returned: if set
      type: dict

    module:
      description: WSGI module to run.
      returned: always
      type: str

    path:
      description: Additional lookup path for Python modules.
      returned: if set
      type: str

    callable:
      description: name of the module-based callable that Unit runs as the app.
      returned: if set
      type: str
      
    home:
      description: Virtual environment in use.
      returned: if set
      type: str

    stdout:
      description: filename where Unit redirects the application’s stdout output.
      returned: if set and I(type) is C(python)
      type: str

    stderr:
      description: filename where Unit redirects the application’s stderr output.
      returned: if set and I(type) is C(python)
      type: str
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, utils
from ..module_utils.client import get_client


def run(params, check_mode):
    client = get_client(params["provider"])
    path = ("config", "applications", params["name"])

    if params["state"] == "absent":
        return utils.delete(client, path, check_mode)

    payload = utils.app_params_to_payload(
        params, "python", "module", "path", "home",
    )

    result = utils.create(client, path, payload, check_mode)
    utils.patch_app_object(result["object"], params["name"])
    return result


def main():
    # AUTOMATIC MODULE ARGUMENTS
    argument_spec = {
        "environment": {"type": "dict"},
        "group": {"type": "str"},
        "home": {"type": "path"},
        "limits": {
            "type": "dict",
            "options": {
                "requests": {"type": "int"},
                "timeout": {"type": "int"},
            },
        },
        "module": {"type": "str"},
        "name": {"required": True, "type": "str"},
        "no_processes": {"type": "int"},
        "path": {"type": "str"},
        "callable": {"type": "str"},
        "processes": {
            "type": "dict",
            "options": {
                "idle_timeout": {"type": "int"},
                "max": {"type": "int"},
                "spare": {"type": "int"},
            },
        },
        "provider": {
            "type": "dict",
            "options": {
                "ca_path": {"type": "path"},
                "endpoint": {"type": "str"},
                "password": {"type": "str"},
                "username": {"type": "str"},
                "verify": {"default": True, "type": "bool"},
            },
            "apply_defaults": True,
        },
        "state": {
            "choices": ["present", "absent"],
            "default": "present",
            "type": "str",
        },
        "user": {"type": "str"},
        "version": {"type": "str"},
        "working_directory": {"type": "path"},
        "stdout": {"type": "path"},
        "stderr": {"type": "path"},
    }
    required_if = [("state", "present", ("module",))]
    mutually_exclusive = [("no_processes", "processes")]
    # AUTOMATIC MODULE ARGUMENTS

    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=argument_spec,
        required_if=required_if,
        mutually_exclusive=mutually_exclusive,
    )

    try:
        module.exit_json(**run(module.params, module.check_mode))
    except errors.UnitError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
