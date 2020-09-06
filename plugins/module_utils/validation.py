# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from .errors import UnitError


def report_error(msgs):
    if msgs:
        raise UnitError("\n".join(msgs))


def validate_pass(client, path):
    segments = path.split("/")
    destination = client.get(["config"] + segments[:2])

    if not destination:
        return ["Destination '{0}' does not exist.".format(path)]

    if (
            segments[0] == "applications" and
            len(segments) == 3 and
            segments[2] not in destination.get("targets", {})
    ):
        return ["PHP application target {0} does not exist.".format(path)]

    return []
