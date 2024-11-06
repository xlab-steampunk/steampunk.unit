# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = """
options:

  name:
    description:
      - Application name.
    required: true
    type: str

  limits:
    description:
      - Set the application's lifecycle parameters.
      - Upstream documentation is available at
        U(https://unit.nginx.org/configuration/#configuration-proc-mgmt-lmts).
    type: dict
    suboptions:

      timeout:
        description:
          - Request timeout in seconds. If an app process exceeds this limit
            while handling a request, Unit alerts it to cancel the request and
            returns an HTTP error to the client.
        type: int

      requests:
        description:
          - Maximum number of requests Unit allows an app process to serve. If
            the limit is reached, the process is restarted; this helps to
            mitigate possible memory leaks or other cumulative issues.
        type: int

  no_processes:
    description:
      - Number of processes that should be running at one time.
      - Mutually exclusive with I(processes).
      - Upstream documentation is available at
        U(https://unit.nginx.org/configuration/#configuration-proc-mgmt-prcs).
    type: int

  processes:
    description:
      - Dynamic process limits.
      - Mutually exclusive with I(no_processes).
      - Upstream documentation is available at
        U(https://unit.nginx.org/configuration/#configuration-proc-mgmt-prcs).
    type: dict
    suboptions:

      max:
        description:
          - Maximum number of application processes that Unit will maintain
            (busy and idle).
        type: int

      spare:
        description:
          - Minimum number of idle processes that Unit tries to reserve for an
            app. When the app is started, spare idle processes are launched;
            Unit assigns incoming requests to existing idle processes, forking
            new idles to maintain the spare level if max allows. As processes
            complete requests and turn idle, Unit terminates extra ones after
            idle_timeout.
        type: int

      idle_timeout:
        description:
          - Time in seconds that Unit waits before terminating an idle process
            which exceeds spare.
        type: int

  working_directory:
    description:
      - The app's working directory. If not set, the Unit daemon's working
        directory is used.
    type: path

  user:
    description:
      - Username that runs the app process. If not set, nobody is used.
    type: str

  group:
    description:
      - Group name that runs the app process. If not set, the user's primary
        group is used.
    type: str

  environment:
    description:
      - Environment variables to be passed to the application.
    type: dict

  stdout:
    description: filename where Unit redirects the application’s stdout output.
    returned: if set and I(type) is C(python)
    type: str

  stderr:
    description: filename where Unit redirects the application’s stderr output.
    returned: if set and I(type) is C(python)
    type: str
"""
