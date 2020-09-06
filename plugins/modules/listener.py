#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: listener
author:
  - Tadej Borovšak (@tadeboro)
short_description: Manage NGINX Unit listener
description:
  - Manage NGINX Unit listener configuration.
  - Upstream docs are at U(https://unit.nginx.org/configuration/#listeners).
extends_documentation_fragment:
  - steampunk.unit.provider
  - steampunk.unit.state
options:
  pattern:
    description:
      - A pattern that listener will listen to. Pattern also serves as an id
        that module uses to enforce state.
    type: str
    required: true
  pass:
    description:
      - Destination that should receive the incomming requests.
      - If the destination is not defined at the time of module's execution,
        module will abort the operation.
      - Required if I(state) is C(present).
    type: str
  tls:
    description:
      - SSL/TLS configuration.
    type: dict
    suboptions:
      certificate:
        description:
          - Name of the certificate chain.
          - If the certificate chain is not already defined, module will
            report an error.
        type: str
"""

EXAMPLES = """
- name: Create new listener (applications/test must exist)
  steampunk.unit.listener:
    pattern: "127.0.0.1:80"
    pass: applications/test

- name: Create new listener (certificate bundle must exist)
  steampunk.unit.listener:
    pattern: "127.0.0.1:80"
    pass: applications/test
    tls:
      certificate: bundle

- name: Delete listener
  steampunk.unit.listener:
    pattern: "*:3000"
    state: absent
"""

RETURN = """
object:
  description: Object representing NGINX Unit listener.
  returned: On success and if I(state) == C(present)
  type: complex
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

from ..module_utils import errors, validation, utils
from ..module_utils.client import get_client


def validate_current_state(client, payload):
    msgs = validation.validate_pass(client, payload["pass"])

    cert = payload.get("tls", {}).get("certificate")
    if cert and not client.get(("certificates", cert)):
        msgs.append("Certificate '{0}' does not exist.".format(cert))

    validation.report_error(msgs)


def run(params, check_mode):
    client = get_client(params["provider"])
    path = ("config", "listeners", params["pattern"])

    if params["state"] == "absent":
        return utils.delete(client, path, check_mode)

    payload = utils.filter_dict(params, "pass", "tls")
    validate_current_state(client, payload)
    result = utils.create(client, path, payload, check_mode)
    result.add_object_fields(pattern=params["pattern"])
    return result


def main():
    # AUTOMATIC MODULE ARGUMENTS
    argument_spec = {
        "pass": {"type": "str"},
        "pattern": {"required": True, "type": "str"},
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
        "tls": {"type": "dict", "options": {"certificate": {"type": "str"}}},
    }
    required_if = [("state", "present", ("pass",))]
    # AUTOMATIC MODULE ARGUMENTS

    # We added no_log=False because Ansible thinks that the pass parameter
    # contains a password. Crazzy bugger ;)
    argument_spec["pass"]["no_log"] = False

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
