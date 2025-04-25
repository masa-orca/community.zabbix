#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2013, Alexander Bulimov <lazywolf0@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: zabbix_maintenance
short_description: Create Zabbix maintenance windows
description:
    - This module will let you create Zabbix maintenance windows.
author: "Alexander Bulimov (@abulimov)"
requirements:
    - "python >= 3.9"
options:
    state:
        description:
            - Create or remove a maintenance window. Maintenance window to remove is identified by name.
        default: present
        choices: [ "present", "absent" ]
        type: str
    host_names:
        description:
            - Hosts to manage maintenance window for.
            - B(Required) option when I(state=present) and I(host_groups) is not used.
        aliases: [ "host_name" ]
        type: list
        elements: str
    host_groups:
        description:
            - Host groups to manage maintenance window for.
            - B(Required) option when I(state=present) and I(host_names) is not used.
        aliases: [ "host_group" ]
        type: list
        elements: str
    append:
        description:
            - Whether to append hosts and host groups to the existing maintenance.
        type: bool
        default: false
    minutes:
        description:
            - Length of maintenance window in minutes.
            - This value will be deprecated after community.zabbix 4.0.0 version.
        default: 10
        type: int
    timeperiods:
        description:
            - Timeperiods of maintenance window.
        type: list
        elements: dict
        suboptions:
            timeperiod_type:
                description:
                    - Type of time period.
                type: str
                default: one_time_only
                choices: [ "one_time_only", "daily", "weekly", "monthly" ]
            start_date:
                description:
                    - Start date of the maintenance window.
                    - This value will be used if I(timeperiod_type=one_time_only).
                    - The date format is YYYY-MM-DD HH:MM.
                    - If not specified, the current date will be used.
                type: str
                choices: [ "one_time_only", "daily", "weekly", "monthly" ]
            start_time:
                description:
                    - Start time of the maintenance window.
                    - This value will be used if I(timeperiod_type=daily), I(timeperiod_type=weekly) or I(timeperiod_type=monthly).
                    - The time format is HH:MM.
                type: str
                default: 00:00
            period:
                description:
                    - Length of the time period in minutes.
                type: int
                default: 0
            every:
                description:
                    - For daily and weekly periods every defines day or week intervals.
                    - For monthly periods every defines month intervals.
                    - This value will be used if I(timeperiod_type=daily), I(timeperiod_type=weekly) or I(timeperiod_type=monthly).
                type: int
                default: 0
            dayofweek:
                description:
                    - For weekly periods dayofweek defines the day of the week.
                type: str
                choices:
                    - first_week
                    - second_week
                    - third_week
                    - fourth_week
                    - last_week
                default: first_week
            day:
                description:
                    - Day of the month.
                    - This value will be required if I(timeperiod_type=monthly) and I(dayofweek) is not defined.
                type: int
            months:
                description:
                    - Month of the year.
                type: list
                elements: str
                choices:
                    - January
                    - February
                    - March
                    - April
                    - May
                    - June
                    - July
                    - August
                    - September
                    - October
                    - November
                    - December

    name:
        description:
            - Unique name of maintenance window.
        required: true
        type: str
    desc:
        description:
            - Short description of maintenance window.
        default: Created by Ansible
        type: str
    collect_data:
        description:
            - Type of maintenance. With data collection, or without.
        type: bool
        default: "yes"
    visible_name:
        description:
            - Type of zabbix host name to use for identifying hosts to include in the maintenance.
            - I(visible_name=yes) to search by visible name,  I(visible_name=no) to search by technical name.
        type: bool
        default: "yes"
    active_since:
        description:
            - Time when the maintenance becomes active.
            - The given value will be rounded down to minutes.
            - Uses `datetime.datetime.now(`) if not specified.
        type: "str"
        default: ""
    active_till:
        description:
            - Time when the maintenance stops being active.
            - The given value will be rounded down to minutes.
            - Gets calculated from I(minutes) if not specified.
        type: "str"
        default: ""
    tags:
        description:
            - List of tags to assign to the hosts in maintenance.
            - Requires I(collect_data=yes).
        type: list
        elements: dict
        suboptions:
            tag:
                description:
                    - Name of the tag.
                type: str
                required: true
            value:
                description:
                    - Value of the tag.
                type: str
                default: ""
            operator:
                description:
                    - Condition operator.
                    - Possible values is
                    - 0 - Equals
                    - 2 - Contains
                type: int
                default: 2
    tags_evaltype:
        description:
            - Problem tag evaluation method.
        type: str
        choices:
            - and_or
            - or
        default: and_or

extends_documentation_fragment:
- community.zabbix.zabbix


notes:
    - Useful for setting hosts in maintenance mode before big update,
      and removing maintenance window after update.
    - Module creates maintenance window from now() to now() + minutes,
      so if Zabbix server's time and host's time are not synchronized,
      you will get strange results.
"""

EXAMPLES = r"""
# If you want to use Username and Password to be authenticated by Zabbix Server
- name: Set credentials to access Zabbix Server API
  ansible.builtin.set_fact:
    ansible_user: Admin
    ansible_httpapi_pass: zabbix

# If you want to use API token to be authenticated by Zabbix Server
# https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/administration/general#api-tokens
- name: Set API token
  ansible.builtin.set_fact:
    ansible_zabbix_auth_key: 8ec0d52432c15c91fcafe9888500cf9a607f44091ab554dbee860f6b44fac895

- name: Create a named maintenance window for host www1 for 90 minutes
  # set task level variables as we change ansible_connection plugin here
  vars:
    ansible_network_os: community.zabbix.zabbix
    ansible_connection: httpapi
    ansible_httpapi_port: 443
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_zabbix_url_path: "zabbixeu"  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
    ansible_host: zabbix-example-fqdn.org
  community.zabbix.zabbix_maintenance:
    name: Update of www1
    host_name: www1.example.com
    state: present
    minutes: 90

- name: Create a named maintenance window for host www1 and host groups Office and Dev
  # set task level variables as we change ansible_connection plugin here
  vars:
    ansible_network_os: community.zabbix.zabbix
    ansible_connection: httpapi
    ansible_httpapi_port: 443
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_zabbix_url_path: "zabbixeu"  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
    ansible_host: zabbix-example-fqdn.org
  community.zabbix.zabbix_maintenance:
    name: Update of www1
    host_name: www1.example.com
    host_groups:
      - Office
      - Dev
    state: present
    tags:
      - tag: ExampleHostsTag
      - tag: ExampleHostsTag2
        value: ExampleTagValue
      - tag: ExampleHostsTag3
        value: ExampleTagValue
        operator: 0

- name: Create a named maintenance window for hosts www1 and db1, without data collection.
  # set task level variables as we change ansible_connection plugin here
  vars:
    ansible_network_os: community.zabbix.zabbix
    ansible_connection: httpapi
    ansible_httpapi_port: 443
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_zabbix_url_path: "zabbixeu"  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
    ansible_host: zabbix-example-fqdn.org
  community.zabbix.zabbix_maintenance:
    name: update
    host_names:
      - www1.example.com
      - db1.example.com
    state: present
    collect_data: false

- name: Remove maintenance window by name
  # set task level variables as we change ansible_connection plugin here
  vars:
    ansible_network_os: community.zabbix.zabbix
    ansible_connection: httpapi
    ansible_httpapi_port: 443
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_zabbix_url_path: "zabbixeu"  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
    ansible_host: zabbix-example-fqdn.org
  community.zabbix.zabbix_maintenance:
    name: Test1
    state: absent

- name: Create maintenance window by date
  # set task level variables as we change ansible_connection plugin here
  vars:
    ansible_network_os: community.zabbix.zabbix
    ansible_connection: httpapi
    ansible_httpapi_port: 443
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_zabbix_url_path: "zabbixeu"  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
    ansible_host: zabbix-example-fqdn.org
  community.zabbix.zabbix_maintenance:
    name: TestDate
    state: present
    host_names:
      - host.example.org
    active_since: "1979-09-19 09:00"
    active_till: "1979-09-19 17:00"
"""

import datetime
import time

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils
from ansible.module_utils.compat.version import LooseVersion


class MaintenanceModule(ZabbixBase):
    def create_maintenance(
        self,
        group_ids,
        host_ids,
        start_time,
        maintenance_type,
        period,
        name,
        desc,
        tags,
    ):
        end_time = start_time + period
        parameters = {
            "groups": [{"groupid": groupid} for groupid in group_ids],
            "hosts": [{"hostid": hostid} for hostid in host_ids],
            "name": name,
            "maintenance_type": maintenance_type,
            "active_since": str(start_time),
            "active_till": str(end_time),
            "description": desc,
            "timeperiods": [
                {
                    "timeperiod_type": "0",
                    "start_date": str(start_time),
                    "period": str(period),
                }
            ],
        }
        if LooseVersion(self._zbx_api_version) < LooseVersion("6.2"):
            parameters["groupids"] = group_ids
            parameters["hostids"] = host_ids
            del parameters["groups"]
            del parameters["hosts"]
        if tags is not None:
            parameters["tags"] = tags
        self._zapi.maintenance.create(parameters)
        return 0, None, None

    def update_maintenance(
        self,
        maintenance_id,
        group_ids,
        host_ids,
        start_time,
        maintenance_type,
        period,
        desc,
        tags,
    ):
        end_time = start_time + period
        parameters = {
            "maintenanceid": maintenance_id,
            "groups": [{"groupid": groupid} for groupid in group_ids],
            "hosts": [{"hostid": hostid} for hostid in host_ids],
            "maintenance_type": maintenance_type,
            "active_since": str(start_time),
            "active_till": str(end_time),
            "description": desc,
            "timeperiods": [
                {
                    "timeperiod_type": "0",
                    "start_date": str(start_time),
                    "period": str(period),
                }
            ],
        }
        if LooseVersion(self._zbx_api_version) < LooseVersion("6.2"):
            parameters["groupids"] = group_ids
            parameters["hostids"] = host_ids
            del parameters["groups"]
            del parameters["hosts"]
        if tags is not None:
            parameters["tags"] = tags
        self._zapi.maintenance.update(parameters)
        return 0, None, None

    def get_maintenance(self, name):
        parameters = {
            "filter": {"name": name},
            "selectHostGroups": "extend",
            "selectHosts": "extend",
            "selectTags": "extend",
        }
        if LooseVersion(self._zbx_api_version) < LooseVersion("6.2"):
            parameters["selectGroups"] = parameters["selectHostGroups"]
            del parameters["selectHostGroups"]
        maintenances = self._zapi.maintenance.get(parameters)

        for maintenance in maintenances:
            maintenance["groupids"] = (
                [group["groupid"] for group in maintenance["hostgroups"]]
                if "hostgroups" in maintenance
                else []
            )
            if LooseVersion(self._zbx_api_version) < LooseVersion("6.2"):
                maintenance["groupids"] = (
                    [group["groupid"] for group in maintenance["groups"]]
                    if "groups" in maintenance
                    else []
                )
            maintenance["hostids"] = (
                [host["hostid"] for host in maintenance["hosts"]]
                if "hosts" in maintenance
                else []
            )
            return 0, maintenance, None

        return 0, None, None

    def delete_maintenance(self, maintenance_id):
        self._zapi.maintenance.delete([maintenance_id])
        return 0, None, None

    def get_group_ids(self, host_groups):
        group_ids = []
        for group in host_groups:
            result = self._zapi.hostgroup.get(
                {"output": "extend", "filter": {"name": group}}
            )

            if not result:
                return 1, None, "Group id for group %s not found" % group

            group_ids.append(result[0]["groupid"])

        return 0, group_ids, None

    def get_host_ids(self, host_names, zabbix_host):
        host_ids = []
        for host in host_names:
            result = self._zapi.host.get(
                {"output": "extend", "filter": {zabbix_host: host}}
            )

            if not result:
                return 1, None, "Host id for host %s not found" % host

            host_ids.append(result[0]["hostid"])

        return 0, host_ids, None

    def check_maint_properties(
        self,
        maintenance,
        group_ids,
        host_ids,
        maintenance_type,
        start_time,
        period,
        desc,
        tags,
    ):
        if sorted(group_ids) != sorted(maintenance["groupids"]):
            return True
        if sorted(host_ids) != sorted(maintenance["hostids"]):
            return True
        if str(maintenance_type) != maintenance["maintenance_type"]:
            return True
        if str(int(start_time)) != maintenance["active_since"]:
            return True
        if str(int(start_time + period)) != maintenance["active_till"]:
            return True
        if str(desc) != maintenance["description"]:
            return True
        if tags is not None and "tags" in maintenance:
            if sorted(tags, key=lambda k: k["tag"]) != sorted(
                maintenance["tags"], key=lambda k: k["tag"]
            ):
                return True


def main():
    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(
                type="str",
                required=False,
                default="present",
                choices=["present", "absent"],
            ),
            host_names=dict(
                type="list",
                required=False,
                default=None,
                aliases=["host_name"],
                elements="str",
            ),
            minutes=dict(type="int", required=False, default=10),
            timeperiods=dict(
                type="list",
                required=False,
                default=None,
                elements="dict",
                options=dict(
                    timeperiod_type=dict(
                        type="str",
                        required=False,
                        default="one_time_only",
                        choices=["one_time_only", "daily", "weekly", "monthly"],
                    ),
                    start_date=dict(type="str", required=False, default=""),
                    start_time=dict(type="str", required=False, default="00:00"),
                    period=dict(type="int", required=False, default=0),
                    every=dict(type="int", required=False, default=0),
                    dayofweek=dict(
                        type="str",
                        required=False,
                        default="first_week",
                        choices=[
                            "first_week",
                            "second_week",
                            "third_week",
                            "fourth_week",
                            "last_week",
                        ],
                    ),
                    day=dict(type="int", required=False, default=0),
                    months=dict(
                        type="list",
                        required=False,
                        default=None,
                        elements="str",
                        choices=[
                            "January",
                            "February",
                            "March",
                            "April",
                            "May",
                            "June",
                            "July",
                            "August",
                            "September",
                            "October",
                            "November",
                            "December",
                        ],
                    ),
                ),
            ),
            host_groups=dict(
                type="list",
                required=False,
                default=None,
                aliases=["host_group"],
                elements="str",
            ),
            append=dict(type="bool", required=False, default=False),
            name=dict(type="str", required=True),
            desc=dict(type="str", required=False, default="Created by Ansible"),
            collect_data=dict(type="bool", required=False, default=True),
            visible_name=dict(type="bool", required=False, default=True),
            active_since=dict(type="str", required=False, default=""),
            active_till=dict(type="str", required=False, default=""),
            tags=dict(
                type="list",
                elements="dict",
                required=False,
                options=dict(
                    tag=dict(type="str", required=True),
                    operator=dict(type="int", default=2),
                    value=dict(type="str", default=""),
                ),
            ),
            tags_evaltype=dict(
                type="str", required=False, default="and_or", choices=["and_or", "or"]
            ),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=[
            ["timeperiods", "minutes"]
        ],
        mutually_exclusive=[
            ["timeperiods", "minutes"]
        ],
        supports_check_mode=True
    )

    maint = MaintenanceModule(module)

    host_names = module.params["host_names"]
    host_groups = module.params["host_groups"]
    append = module.params["append"]
    state = module.params["state"]
    minutes = module.params["minutes"]
    timeperiods = module.params["timeperiods"]
    name = module.params["name"]
    desc = module.params["desc"]
    collect_data = module.params["collect_data"]
    visible_name = module.params["visible_name"]
    active_since = module.params["active_since"]
    active_till = module.params["active_till"]
    tags = module.params["tags"]
    tags_evaltype = module.params["tags_evaltype"]

    if collect_data:
        maintenance_type = 0
    else:
        maintenance_type = 1
        if tags is not None:
            module.fail_json(
                msg="Tags cannot be provided for maintenance without data collection."
            )

    if visible_name:
        zabbix_host = "name"
    else:
        zabbix_host = "host"

    changed = False

    if state == "present":
        if not host_names and not host_groups:
            module.fail_json(
                msg="At least one host_name or host_group must be defined for each created maintenance."
            )

        now = (
            datetime.datetime.fromisoformat(active_since)
            if active_since != ""
            else datetime.datetime.now().replace(second=0)
        )
        start_time = int(time.mktime(now.timetuple()))
        period = (
            int((datetime.datetime.fromisoformat(active_till) - now).total_seconds())
            if active_till != ""
            else 60 * int(minutes)
        )  # N * 60 seconds

        if host_groups:
            (rc, group_ids, error) = maint.get_group_ids(host_groups)
            if rc != 0:
                module.fail_json(msg="Failed to get group_ids: %s" % error)
        else:
            group_ids = []

        if host_names:
            (rc, host_ids, error) = maint.get_host_ids(host_names, zabbix_host)
            if rc != 0:
                module.fail_json(msg="Failed to get host_ids: %s" % error)
        else:
            host_ids = []

        (rc, maintenance, error) = maint.get_maintenance(name)
        if rc != 0:
            module.fail_json(
                msg="Failed to check maintenance %s existence: %s" % (name, error)
            )

        if maintenance:
            if append:
                group_ids = list(set(group_ids + maintenance["groupids"]))
                host_ids = list(set(host_ids + maintenance["hostids"]))

            if maint.check_maint_properties(
                maintenance,
                group_ids,
                host_ids,
                maintenance_type,
                start_time,
                period,
                desc,
                tags,
            ):
                if module.check_mode:
                    changed = True
                else:
                    (rc, data, error) = maint.update_maintenance(
                        maintenance["maintenanceid"],
                        group_ids,
                        host_ids,
                        start_time,
                        maintenance_type,
                        period,
                        desc,
                        tags,
                    )
                    if rc == 0:
                        changed = True
                    else:
                        module.fail_json(msg="Failed to update maintenance: %s" % error)

        if not maintenance:
            if module.check_mode:
                changed = True
            else:
                (rc, data, error) = maint.create_maintenance(
                    group_ids,
                    host_ids,
                    start_time,
                    maintenance_type,
                    period,
                    name,
                    desc,
                    tags,
                )
                if rc == 0:
                    changed = True
                else:
                    module.fail_json(msg="Failed to create maintenance: %s" % error)

    if state == "absent":

        (rc, maintenance, error) = maint.get_maintenance(name)
        if rc != 0:
            module.fail_json(
                msg="Failed to check maintenance %s existence: %s" % (name, error)
            )

        if maintenance:
            if module.check_mode:
                changed = True
            else:
                (rc, data, error) = maint.delete_maintenance(
                    maintenance["maintenanceid"]
                )
                if rc == 0:
                    changed = True
                else:
                    module.fail_json(msg="Failed to remove maintenance: %s" % error)

    module.exit_json(changed=changed)


if __name__ == "__main__":
    main()
