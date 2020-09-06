#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: route
author:
  - Tadej Borovšak (@tadeboro)
short_description: Manage NGINX Unit route
description:
  - Manage NGINX Unit route configuration.
  - Upstream docs are at U(https://unit.nginx.org/configuration/#routes).
extends_documentation_fragment:
  - steampunk.unit.provider
  - steampunk.unit.state
options:
  name:
    description:
      - Name of the route to manage.
      - Required if I(global) is C(false). If I(global) is C(true), this
        parameter is ignored.
    type: str
  global:
    description:
      - Do not create or delete named routes and act on a global route.
    default: false
    type: bool
  steps:
    description:
      - Route steps that are matched sequentially.
      - Required if I(state) is C(present).
    type: list
    elements: dict
    suboptions:
      match:
        description:
          - Step's conditions to be matched.
          - See U(https://unit.nginx.org/configuration/#condition-matching)
            for more details about matching, case sensitivity of matches, etc.
        type: dict
        suboptions:
          arguments:
            description:
              - Parameter arguments supplied in the request URI.
              - See U(https://unit.nginx.org/configuration/#compound-matching)
                for more information about the format and semantics.
            type: list
            elements: dict
          cookies:
            description:
              - Cookies supplied with the request.
              - See U(https://unit.nginx.org/configuration/#compound-matching)
                for more information about the format and semantics.
            type: list
            elements: dict
          destination:
            description:
              - Target IP address and optional port of the request.
              - See U(https://unit.nginx.org/configuration/#simple-matching)
                for more information about the format and semantics.
            type: list
            elements: str
          headers:
            description:
              - Header fields supplied with the request.
              - See U(https://unit.nginx.org/configuration/#compound-matching)
                for more information about the format and semantics.
            type: list
            elements: dict
          host:
            description:
              - Host from the Host header field without port number,
                normalized by removing the trailing period (if any).
              - See U(https://unit.nginx.org/configuration/#simple-matching)
                for more information about the format and semantics.
            type: list
            elements: str
          method:
            description:
              - Method from the request line.
              - See U(https://unit.nginx.org/configuration/#simple-matching)
                for more information about the format and semantics.
            type: list
            elements: str
          scheme:
            description:
              - URI scheme.
              - See U(https://unit.nginx.org/configuration/#simple-matching)
                for more information about the format and semantics.
            type: str
            choices: [ http, https ]
          source:
            description:
              - Source IP address and optional port of the request.
              - See U(https://unit.nginx.org/configuration/#simple-matching)
                for more information about the format and semantics.
            type: list
            elements: str
          uri:
            description:
              - URI path without arguments.
              - See U(https://unit.nginx.org/configuration/#simple-matching)
                for more information about the format and semantics.
            type: list
            elements: str
      action:
        description:
          - Action to take if the step's matches.
          - See U(https://unit.nginx.org/configuration/#request-handling) for
            more details about all possible combinations of options.
        required: true
        type: dict
        suboptions:
          pass:
            description:
              - Route's destination.
            type: str
          share:
            description:
              - A static path from where files are served upon a match.
              - Use I(fallback) option to specify what happens if the path is
                not accessible.
            type: str
          fallback:
            description:
              - A fallback route step that is taken if the file listed in the
                I(static) parameter is not found or cannot be accessed.
              - Format of this field is a nested route step. See nested
                routing example for more information about the format.
            type: dict
          proxy:
            description:
              - Socket address of an HTTP server where the request is proxied.
            type: str
          return:
            description:
              - The HTTP response status code to be returned.
              - Use the I(location) paramter to specfy redirection target if
                status code implies one.
            type: int
          location:
            description:
              - The location taht request should be redirected to.
            type: str
"""

EXAMPLES = """
- name: Route with a complex matching rule step and a static fallback step
  steampunk.unit.route:
    name: complex
    steps:
      - match:
          uri: /admin/*
          scheme: https
          arguments:
            mode: strict
            access: "!raw"
          cookies:
            user_role: admin
        action:
          pass: applications/cms
      - action:
          share: /www/static/


- name: Global routes for an imaginary blog site
  steampunk.unit.route:
    global: true
    steps:
      - match:
          host: blog.example.com/admin
          source: "*:8000-9000"
        action:
          pass: applications/blogs/admin
      - match:
          host:
            - blog.example.com
            - blog.*.org
          source: "*:8000-9000"
        action:
          pass: applications/blogs/core

- name: Static file serving with fallbacks
  steampunk.unit.route:
    name: static-site
    steps:
      - action:
          share: /www/static/
          fallback:
            share: /old/static/
            fallback:
              return 404
"""

RETURN = """
object:
  description: Object representing NGINX Unit route.
  returned: On success and if I(state) == C(present)
  type: dict
  contains:
    name:
      description: Route name (can be C(None) for global routes).
      returned: always
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

from ..module_utils import errors, validation, utils
from ..module_utils.client import get_client


def validate_action(client, action):
    msgs = []

    if "pass" in action and action["pass"]:
        msgs.extend(validation.validate_pass(client, action["pass"]))
    if "fallback" in action and action["fallback"]:
        msgs.extend(validate_action(client, action["fallback"]))

    return msgs


def validate_current_state(client, steps):
    msgs = []

    for i, step in enumerate(steps):
        action = step.get("action")
        if not action:
            msgs.append("Missing action field in step {0}".format(i))
        else:
            msgs.extend(validate_action(client, action))

    validation.report_error(msgs)


def build_payload(steps):
    return [
        dict(
            (k, utils.compact_dict(v))  # Remove None values from match/action
            for k, v in utils.compact_dict(s).items()  # Remove empty matches
        ) for s in steps
    ]


def run(params, check_mode):
    client = get_client(params["provider"])
    if params["global"]:
        path = ("config", "routes")
    else:
        path = ("config", "routes", params["name"])

    if params["state"] == "present":
        payload = build_payload(params["steps"])
        validate_current_state(client, payload)
        result = utils.create(client, path, payload, check_mode)

        # Route object is a bit different because normally it would be
        # just an array of steps, which is useless for consumers. This is
        # why we "wrap" the array into object that can contain some more
        # metadata.
        result["object"] = dict(name=params["name"], steps=result["object"])
    else:
        result = utils.delete(client, path, check_mode)

    return result


def main():
    # AUTOMATIC MODULE ARGUMENTS
    argument_spec = {
        "global": {"default": False, "type": "bool"},
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
        "state": {
            "choices": ["present", "absent"],
            "default": "present",
            "type": "str",
        },
        "steps": {
            "elements": "dict",
            "type": "list",
            "options": {
                "action": {
                    "required": True,
                    "type": "dict",
                    "options": {
                        "fallback": {"type": "dict"},
                        "location": {"type": "str"},
                        "pass": {"type": "str"},
                        "proxy": {"type": "str"},
                        "return": {"type": "int"},
                        "share": {"type": "str"},
                    },
                },
                "match": {
                    "type": "dict",
                    "options": {
                        "arguments": {"elements": "dict", "type": "list"},
                        "cookies": {"elements": "dict", "type": "list"},
                        "destination": {"elements": "str", "type": "list"},
                        "headers": {"elements": "dict", "type": "list"},
                        "host": {"elements": "str", "type": "list"},
                        "method": {"elements": "str", "type": "list"},
                        "scheme": {
                            "choices": ["http", "https"],
                            "type": "str",
                        },
                        "source": {"elements": "str", "type": "list"},
                        "uri": {"elements": "str", "type": "list"},
                    },
                },
            },
        },
    }
    required_if = [
        ("global", False, ("name",)),
        ("state", "present", ("steps",)),
    ]
    # AUTOMATIC MODULE ARGUMENTS

    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=argument_spec,
        required_if=required_if,
    )

    try:
        module.exit_json(**run(module.params, module.check_mode))
    except errors.UnitError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
