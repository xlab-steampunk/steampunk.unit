#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: route_info
author:
  - Tadej Borovšak (@tadeboro)
short_description: Retrieve NGINX Unit route(s)
description:
  - Retrieve information about all NGINX Unit routes of about a speficic one.
  - Upstream docs are at U(https://unit.nginx.org/configuration/#routes).
extends_documentation_fragment:
  - steampunk.unit.provider
options:
  name:
    description:
      - Name of the route to retrieve. If parameter is not specified, retrieve
        information about all routes.
    type: str
"""

EXAMPLES = """
- name: Retrieve information about all routes
  steampunk.unit.route_info:

- name: Retrieve information about a specific route
  steampunk.unit.route:
    name: static-site
"""

RETURN = """
objects:
  description: Object representing NGINX Unit route.
  returned: On success and if I(state) == C(present)
  type: list
  elements: dict
  contains:
    name:
      description: Route name.
      returned: if I(global) == C(false)
      type: str
      sample: my-route
    steps:
      description: List of steps in route
      returned: always
      type: list
      elements: dict
      contains:
        match:
          description: Step's conditions to be matched.
          type: dict
          returned: if specified
          contains:
            arguments:
              description: Parameter arguments supplied in the request URI.
              returned: if specified
              type: list
              elements: dict
            cookies:
              description: Cookies supplied with the request.
              returned: if specified
              type: list
              elements: dict
            destination:
              description: Target IP address and optional port of the request.
              returned: if specified
              type: list
              elements: str
            headers:
              description: Header fields supplied with the request.
              returned: if specified
              type: list
              elements: dict
            host:
              description: Host from the Host header field without port number.
              returned: if specified
              type: list
              elements: str
            method:
              description: Method from the request line.
              returned: if specified
              type: list
              elements: str
            scheme:
              description: URI scheme.
              returned: if specified
              type: str
            source:
              description: Source IP address and optional port of the request.
              returned: if specified
              type: list
              elements: str
            uri:
              description: URI path without arguments.
              returned: if specified
              type: list
              elements: str
        action:
          description: Action to take if the step's matches.
          returned: always
          type: dict
          contains:
            pass:
              description: Route's destination.
              returned: if specified
              type: str
            share:
              description: >-
                A static path from where files are served upon a match.
              returned: if specified
              type: str
            fallback:
              description: A fallback route step.
              returned: if specified
              type: dict
            proxy:
              description: >-
                Socket address of an HTTP server where the request is proxied.
              returned: if specified
              type: str
            return:
              description: The HTTP response status code to be returned.
              returned: if specified
              type: int
            location:
              description: The location taht request should be redirected to.
              returned: if specified
              type: str
"""

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import errors
from ..module_utils.client import get_client


def run(params):
    client = get_client(params["provider"])
    if params["name"]:
        route = client.get(("config", "routes", params["name"]))
        objects = [dict(name=params["name"], steps=route)] if route else []
    else:
        routes = client.get(("config", "routes"))
        if isinstance(routes, dict):
            # Multiple named routes
            objects = [dict(name=n, steps=s) for n, s in routes.items()]
        else:
            # Single global route
            objects = [dict(name=None, steps=routes)]

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
