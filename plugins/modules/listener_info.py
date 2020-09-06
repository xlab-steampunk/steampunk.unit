#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: listener_info
author:
  - Tadej Borovšak (@tadeboro)
short_description: List NGINX Unit listener(s)
description:
  - Retrieve NGINX Unit listener configuration.
  - Upstream docs are at U(https://unit.nginx.org/configuration/#listeners).
extends_documentation_fragment:
  - steampunk.unit.provider
options:
  pattern:
    description:
      - A pattern to retrieve information about. Retrieve all listeners of not
        set.
    type: str
"""

EXAMPLES = """
- name: Retrieve information about all listeners
  steampunk.unit.listener_info:

- name: Retrieve information about a specific listener
  steampunk.unit.listener:
    pattern: "127.0.0.1:80"
"""

RETURN = """
objects:
  description: Objects representing NGINX Unit listeners.
  returned: always
  type: list
  elements: dict
  contains:
    pattern:
      description: Listener pattern.
      returned: always
      type: str
      sample: 127.0.0.1:3000
    pass:
      description: Destination for incomming requests.
      returned: always
      type: str
      sample: applications/test
    tls:
      description: SSL/TLS configuration
      returned: if set
      type: complex
      contains:
        certificate:
          description: Certificate bundle
          returned: always
          type: str
          sample: certificates/my-bundle
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors
from ..module_utils.client import get_client


def run(params):
    client = get_client(params["provider"])
    if params["pattern"]:
        listener = client.get(("config", "listeners", params["pattern"]))
        objects = [
            dict(listener, pattern=params["pattern"])
        ] if listener else []
    else:
        listeners = client.get(("config", "listeners"))
        objects = [dict(l, pattern=p) for p, l in listeners.items()]

    return dict(changed=False, objects=objects)


def main():
    # AUTOMATIC MODULE ARGUMENTS
    argument_spec = {
        "pattern": {"type": "str"},
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
