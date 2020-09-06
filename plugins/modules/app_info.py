#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: app_info
author:
  - Tadej Borovšak (@tadeboro)
short_description: Retrieve information about configured applications
description:
  - Retrieve NGINX Unit application configuration.
  - Upstream docs are at U(https://unit.nginx.org/configuration/#python).
extends_documentation_fragment:
  - steampunk.unit.provider
options:
  name:
    description:
      - Name of the application to retrieve. If parameter is not specified,
        retrieve information about all applications.
    type: str
"""

EXAMPLES = """
- name: Retrieve information about all applications
  steampunk.unit.app_info:

- name: Retrieve information about a specific application
  steampunk.unit.app_info:
    name: sample_app
"""

RETURN = """
object:
  description: Object representing NGINX Unit application.
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
      returned: if I(type) is C(python)
      type: str

    path:
      description: Additional lookup path for Python modules.
      returned: if set and I(type) is C(python)
      type: str

    home:
      description: Virtual environment in use.
      returned: if set and I(type) is C(python)
      type: str
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors, utils
from ..module_utils.client import get_client


def run(params):
    client = get_client(params["provider"])
    if params["name"]:
        app = client.get(("config", "applications", params["name"]))
        objects = [
            utils.patch_app_object(app, params["name"])
        ] if app else []
    else:
        apps = client.get(("config", "applications"))
        objects = [utils.patch_app_object(a, n) for n, a in apps.items()]

    return dict(changed=False, objects=objects)


def main():
    # AUTOMATIC MODULE ARGUMENTS
    argument_spec = {
        "name": {"type": "str"},
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
    }
    # AUTOMATIC MODULE ARGUMENTS

    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=argument_spec,
    )

    try:
        module.exit_json(**run(module.params))
    except errors.UnitError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
