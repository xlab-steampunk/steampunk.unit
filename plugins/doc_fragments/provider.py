# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = """
options:
  provider:
    description:
      - Connection parameters.
    type: dict
    suboptions:

      endpoint:
        description:
          - HTTP or UNIX uri that should be used to communicate with the Unit.
          - The uri B(MUST) be prefixed by either C(http://), C(https://), or
            C(unix://).
          - By default, modules will try to connect to
            I(unix:///var/run/unit/control.sock), and if this socket does not
            exist, fallback to I(unix:///var/run/control.unit.sock).
          - Can also be set using the I(UNIT_ENDPOINT) environment variable.
        type: str

      username:
        description:
          - Username that is used when the I(enpoint) is protected using the
            basic authentication.
          - This parameter is ignored when the I(enpoint) parameter points to
            an unix socket.
          - Can also be set using the I(UNIT_ENDPOINT) environment variable.
        type: str

      password:
        description:
          - Password that is used when the I(endpoint) is protected using the
            basic authentication.
          - This parameter is ignored when the I(enpoint) parameter points to
            an unix socket.
          - Value is masked in the logs.
          - Can also be set using the I(UNIT_ENDPOINT) environment variable.
        type: str

      verify:
        description:
          - Flag that controls the certificate validation.
          - If you are using self-signed certificates, you can set this
            parameter to C(false).
          - ONLY USE THIS PARAMETER IN DEVELOPMENT SCENARIOS! In you use
            self-signed certificates in production, see the I(auth.ca_path)
            parameter.
          - Can also be set using the  I(UNIT_VERIFY) environment variable.
        type: bool
        default: true

      ca_path:
        description:
          - Path to the CA bundle that should be used to validate the backend
            certificate.
          - If this parameter is not set, module will use the CA bundle that
            python is using.
          - Can also be set using the  I(UNIT_CA_PATH) environment variable.
        type: path
"""
