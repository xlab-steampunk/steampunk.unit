# -*- coding: utf-8 -*-
# Copyright: (c) 2020, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class Result(dict):
    def __init__(self, current, desired):
        super(Result, self).__init__()

        self["changed"] = current != desired
        self["diff"] = dict(before=current, after=desired)
        self["object"] = desired

    @property
    def changed(self):
        return self["changed"]

    def add_object_fields(self, **kwargs):
        self["object"].update(kwargs)


def create(client, path, payload, check_mode):
    result = Result(client.get(path), payload)
    if result.changed and not check_mode:
        client.put(path, payload)
    return result


def delete(client, path, check_mode):
    result = Result(client.get(path), {})
    if result.changed and not check_mode:
        client.delete(path)
    return result


def filter_dict(input, *keys):
    return dict((k, v) for k, v in compact_dict(input).items() if k in keys)


def compact_dict(input):
    return dict((k, v) for k, v in input.items() if v is not None)


def app_params_to_payload(params, typ, *extras):
    payload = filter_dict(
        params, "limits", "processes", "working_directory", "user", "group",
        "environment", *extras
    )

    payload["type"] = typ
    if params["version"]:
        payload["type"] += " " + params["version"]

    if params["no_processes"]:
        payload["processes"] = params["no_processes"]

    return payload


def patch_app_object(app, name):
    app["name"] = name
    if isinstance(app.get("processes"), int):
        app["no_processes"] = app["processes"]
        del app["processes"]
    return app
