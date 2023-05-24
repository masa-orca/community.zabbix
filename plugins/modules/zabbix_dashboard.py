#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2023, ONODERA Masaru <masaru-onodera@ieee.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: zabbix_dashboard

short_description: Create/Update and Delete Zabbix dashboard.

description:
    - This module allows you to create, update amd delete Zabbix dashboard.

author:
    - ONODERA Masaru(@masa-orca)

requirements:
    - "python >= 3.9"

version_added: 2.1.0

options:
    name:
        description:
            - Name of the dashboard.
        required: true
        type: str
    owner:
        description:
            - Username of owner of the dashboard.
        required: false
        type: str
    private:
        description:
            - The dashboard become private if C(true).
        required: false
        type: bool
    default_display_period:
        description:
            - Seconds of default page display period.
        required: false
        type: int
        choices:
            - 10
            - 30
            - 60
            - 120
            - 600
            - 1800
            - 3600
    auto_start:
        description:
            - Slideshow stars automatically if C(true).
        required: false
        type: bool
    pages:
        type: list
        elements: dict
        description:
            - Pages of the dashboard.
        suboptions:
            name:
                description:
                    - Name of the page.
                required: false
                type: str
            display_period:
                description:
                    - Seconds of page display period.
                    - If C(0), the Zabbix uses value of I(dedault_display_period).
                required: false
                type: int
                choices:
                    - 0
                    - 10
                    - 30
                    - 60
                    - 120
                    - 600
                    - 1800
                    - 3600
                default: 0
            widgets:
                type: list
                elements: dict
                description:
                    - Widgets of the dashboard.
                suboptions:
                    type:
                        description:
                            - Type of the widget.
                        required: true
                        type: str
                        choices:
                            - clock
                            - dataover
                            - discovery
                            - favgraphs
                            - favmaps
                            - graph
                            - graphprototype
                            - hostavail
                            - item
                            - map
                            - navtree
                            - plaintext
                            - problemhosts
                            - problems
                            - problemsbysv
                            - slareport
                            - svggraph
                            - systeminfo
                            - tophosts
                            - trigover
                            - url
                            - web
                    name:
                        description:
                            - Custom name of the widget.
                        required: false
                        type: str
                    x:
                        description:
                            - A horizontal position
                        required: false
                        type: int
                    y:
                        description:
                            - A vertical position
                        required: false
                        type: int
                    width:
                        description:
                            - Width of the widget
                        required: false
                        type: int
                    height:
                        description:
                            - Height of the widget
                        required: false
                        type: int
                    view_mode:
                        description:
                            - Header of the widget always appears if C(true).
                        required: false
                        type: bool
                        default: true
                    fields:
                        type: list
                        elements: dict
                        description:
                            - Fields of the dashboard.
                            - Please refer official document about parameter.
                            - U(https://www.zabbix.com/documentation/current/en/manual/api/reference/dashboard/widget_fields)
                        suboptions:
                            type:
                                description:
                                    - Type of the field.
                                required: true
                                type: str
                                choices:
                                    - integer
                                    - string
                                    - host_group
                                    - host
                                    - item
                                    - item_prototype
                                    - graph
                                    - graph_prototype
                                    - map
                                    - service
                                    - sla
                                    - user
                                    - action
                                    - media_type
                            name:
                                description:
                                    - Name of the field.
                                required: true
                                type: str
                            value:
                                description:
                                    - Value of the field.
                                    - This parameter is required if I(type=integer) or I(type=string).
                                required: false
                                type: str
                            value_name:
                                description:
                                    - A name for value of the field.
                                    - This parameter is required if I(type!=integer) and I(type!=string).
                                required: false
                                type: str
                            value_key:
                                description:
                                    - A key for value of the field.
                                    - This parameter is required if I(type=item) or I(type=item_prototype).
                                required: false
                                type: str
                            value_host:
                                description:
                                    - A host name. This parameter is used for filtering value of the field.
                                    - For example, if I(type=item) and I(value_host="Zabbix server"), This module searches item key from item list of Zabbix server.
                                    - This parameter is required if I(type=item) or I(type=item_prototype) or I(type=graph) or I(type=graph_prototype).
                                required: false
                                type: str
extends_documentation_fragment:
    - community.zabbix.zabbix
"""

EXAMPLES = """
# If you want to use Username and Password to be authenticated by Zabbix Server
- name: Set credentials to access Zabbix Server API
  set_fact:
    ansible_user: Admin
    ansible_httpapi_pass: zabbix

# If you want to use API token to be authenticated by Zabbix Server
# https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/administration/general#api-tokens
- name: Set API token
  set_fact:
    ansible_zabbix_auth_key: 8ec0d52432c15c91fcafe9888500cf9a607f44091ab554dbee860f6b44fac895

- name: Update all setting setting (Zabbix <= 6.0)
  # set task level variables as we change ansible_connection plugin here
  vars:
    ansible_network_os: community.zabbix.zabbix
    ansible_connection: httpapi
    ansible_httpapi_port: 443
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_zabbix_url_path: "zabbixeu"  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
    ansible_host: zabbix-example-fqdn.org
  zabbix_settings:


"""

RETURN = """
msg:
    description: The result of the operation
    returned: success
    type: str
    sample: "Successfully update global settings"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils


class Dashboard(ZabbixBase):
    def get_dashboard(self, name):
        try:
            dashboard = self._zapi.dashboard.get(
                {
                    "output": "extend",
                    "selectPages": "extend",
                    "selectUsers": "extend",
                    "selectUserGroups": "extend",
                    "filter": {"name": name},
                }
            )
            self._module.fail_json(msg=dashboard)
        except Exception as e:
            self._module.fail_json(msg="Failed to update global settings: %s" % e)

    # def create_dashboard(
    #     self, name, owner, private, default_display_period, auto_start
    # ):
    #     pass


def main():
    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type="str", required=True),
            owner=dict(type="str"),
            private=dict(type="bool"),
            default_display_period=dict(
                type="int", choices=[10, 30, 60, 120, 600, 1800, 3600]
            ),
            auto_start=dict(type="bool"),
            pages=dict(
                type="list",
                elements="dict",
                options=dict(
                    name=dict(type="str"),
                    display_period=dict(
                        type="int",
                        choices=[0, 10, 30, 60, 120, 600, 1800, 3600],
                        default=0,
                    ),
                    widgets=dict(
                        type="list",
                        elements="dict",
                        options=dict(
                            type=dict(
                                type="str",
                                choices=[
                                    "clock",
                                    "dataover",
                                    "discovery",
                                    "favgraphs",
                                    "favmaps",
                                    "graph",
                                    "graphprototype",
                                    "hostavail",
                                    "item",
                                    "map",
                                    "navtree",
                                    "plaintext",
                                    "problemhosts",
                                    "problems",
                                    "problemsbysv",
                                    "slareport",
                                    "svggraph",
                                    "systeminfo",
                                    "tophosts",
                                    "trigover",
                                    "url",
                                    "web",
                                ],
                            ),
                            name=dict(type="str"),
                            x=dict(type="int"),
                            y=dict(type="int"),
                            width=dict(type="int"),
                            height=dict(type="int"),
                            view_mode=dict(type="bool"),
                            fields=dict(
                                type="list",
                                elements="dict",
                                options=dict(
                                    type=dict(
                                        type="str",
                                        required=True,
                                        choices=[
                                            "integer",
                                            "string",
                                            "host_group",
                                            "host",
                                            "item",
                                            "item_prototype",
                                            "graph",
                                            "graph_prototype",
                                            "map",
                                            "service",
                                            "sla",
                                            "user",
                                            "action",
                                            "media_type",
                                        ],
                                    ),
                                    name=dict(type="str", required=True),
                                    value=dict(
                                        type="str",
                                    ),
                                    value_name=dict(
                                        type="str",
                                    ),
                                    value_key=dict(
                                        type="str",
                                    ),
                                    value_host=dict(
                                        type="str",
                                    ),
                                ),
                                required_if=[
                                    ["type", "integer", ["value"]],
                                    ["type", "string", ["value"]],
                                    ["type", "host_group", ["value_name"]],
                                    ["type", "host", ["value_name"]],
                                    ["type", "item", ["value_key", "value_host"]],
                                    [
                                        "type",
                                        "item_prototype",
                                        ["value_key", "value_host"],
                                    ],
                                    ["type", "graph", ["value_name", "value_host"]],
                                    [
                                        "type",
                                        "graph_prototype",
                                        ["value_name", "value_host"],
                                    ],
                                    ["type", "map", ["value_name"]],
                                    ["type", "service", ["value_name"]],
                                    ["type", "sla", ["value_name"]],
                                    ["type", "user", ["value_name"]],
                                    ["type", "action", ["value_name"]],
                                    ["type", "media_type", ["value_name"]],
                                ],
                            ),
                        ),
                    ),
                ),
            ),
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # name = module.params["name"]
    # owner = module.params["owner"]
    # private = module.params["private"]
    # default_display_period = module.params["default_display_period"]
    # auto_start = module.params["auto_start"]

    # dashboard_class_obj = Dashboard(module)

    # # dashboard = dashboard_class_obj.get_dashboard(name)

    # dashboard_class_obj.create_dashboard(
    #     name, owner, private, default_display_period, auto_start
    # )


if __name__ == "__main__":
    main()
