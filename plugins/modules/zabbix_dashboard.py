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
    display_period:
        description:
            - Seconds of page display period.
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

import re

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
from ansible.module_utils.compat.version import LooseVersion
import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils


class Dashboard(ZabbixBase):
    def get_dashboard(self, name):
        try:
            dashboard = self._zapi.dashboard.get({
                "output": "extend",
                "selectPages": "extend",
                "selectUsers": "extend",
                "selectUserGroups": "extend",
                "filter": {
                    "name": name
                }
            })
            self._module.fail_json(
                msg=dashboard
            )
        except Exception as e:
            self._module.fail_json(msg="Failed to update global settings: %s" % e)


def main():
    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type="str"),
            owner=dict(type="str"),
            private=dict(
                type="bool"
            ),
            display_period=dict(type="int"),
            auto_start=dict(type="bool"),
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    name = module.params["name"]
    owner = module.params["owner"]
    private = module.params["private"]
    display_period = module.params["display_period"]
    auto_start = module.params["auto_start"]

    dashboard_class_obj = Dashboard(module)

    dashboard = dashboard_class_obj.get_dashboard(name)


if __name__ == "__main__":
    main()
