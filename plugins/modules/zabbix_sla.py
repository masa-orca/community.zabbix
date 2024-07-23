#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, ONODERA Masaru <masaru-onodera@ieee.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: zabbix_correlation

short_description: Create/update/delete Zabbix SLA


description:
    - This module allows you to create, update and delete Zabbix SLA.

author:
    - ONODERA Masaru(@masa-orca)

requirements:
    - "python >= 3.9"

version_added: 2.4.0

options:
    name:
        description:
            - Name of this SLA
        type: str
        required: true
    description:
        description:
            - Description of this SLA
        type: str
    period:
        description:
            - A reporting period of this SLA.
        type: str
        choices:
            - daily
            - weekly
            - monthly
            - quarterly
            - annually
    slo:
        description:
            - Minimum acceptable Service Level Objective expressed as a percent.
        type: float
    effective_date:
        description:
            - Effective date of the SLA.
            - Possible values: date timestamp in UTC.
        type: str
    timezone:
        description:
            - Reporting time zone, for example: Europe/London, UTC.
        type: str
    schedule:
        description:
            - The SLA schedule object defines periods where the connected service(s) are scheduled to be in working order.
        type: list
        elements: dict
        suboptions:
            period_from:
                description:
                    - Starting time of the recurrent weekly period of time (inclusive).
                    - Possible values: number of seconds (counting from Sunday).
                type: int
                required: true
            period_to:
                description:
                    - 	Ending time of the recurrent weekly period of time (exclusive).
                    - Possible values: number of seconds (counting from Sunday).
                type: int
                required: true
    service_tags:
        description:
            - The SLA service tag object links services to include in the calculations for the SLA.
        type: list
        elements: dict
        suboptions:
            tag:
                description:
                    - SLA service tag name.
                type: str
                required: true
            operator:
                description:
                    - SLA service tag operator.
                type: str
                choices:
                    - equals
                    - contains
            value:
                description:
                    - SLA service tag value.
                type: str
    excluded_downtimes:
        description:
            - Periods where the connected service(s) are scheduled to be out of working order, without affecting SLI.
        type: list
        elements: dict
        suboptions:
            name:
                description:
                    - Name of the excluded downtime.
                type: str
                required: true
            period_from:
                description:
                    - Starting time of the excluded downtime (inclusive).
                    - Possible values: timestamp.
                type: int
                required: true
            period_to:
                description:
                    - Ending time of the excluded downtime (exclusive).
                    - Possible values: timestamp.
                type: int
                required: true
    status:
        description:
            - Status of the SLA.
        choices:
            - enabled
            - disabled
        default: enabled
        type: str
    state:
        description:
            - State of the SLA.
        type: str
        choices:
            - present
            - absent
        default: present

extends_documentation_fragment:
    - community.zabbix.zabbix

"""

EXAMPLES = """
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

- name: Create correlation of 'New event tag correlation'
  # set task level variables as we change ansible_connection plugin here
  vars:
    ansible_network_os: community.zabbix.zabbix
    ansible_connection: httpapi
    ansible_httpapi_port: 443
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_zabbix_url_path: 'zabbixeu'  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
    ansible_host: zabbix-example-fqdn.org
  community.zabbix.zabbix_correlation:
    name: New event tag correlation
    filter:
      evaltype: and_or
      conditions:
        - type: new_event_tag
          tag: ok
    operations:
      - type: close_old_events
"""

RETURN = """
msg:
    description: The result of the operation
    returned: success
    type: str
    sample: 'Successfully created correlation'
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils


class Sla(ZabbixBase):
    def __init__(self, module, zbx=None, zapi_wrapper=None):
        super(Sla, self).__init__(module, zbx, zapi_wrapper)

    def get_slas(self, sla_name):
        try:
            slas = self._zapi.correlation.get(
                {
                    "output": "extend",
                    "selectSchedule": ["period_from", "period_to"],
                    "selectExcludedDowntimes": ["name", "period_from", "period_to"],
                    "selectServiceTags": ["tag", "operator", "value"],
                    "filter": {"name": sla_name},
                }
            )
            if len(slas) >= 2:
                self._module.fail_json("Too many SLAs are matched.")
            return slas
        except Exception as e:
            self._module.fail_json(
                msg="Failed to get SLA: %s" % e
            )

    def delete_sla(self, sla):
        try:
            parameter = [sla["slaid"]]
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.sla.delete(parameter)
            self._module.exit_json(
                changed=True, msg="Successfully deleted SLA."
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to delete SLA: %s" % e
            )

    def _convert_operations_to_json(self, operations):
        operation_type_values = ["close_old_events", "close_new_event"]

        operations_json = []
        for operation in operations:
            operation_json = {}
            operation_type = zabbix_utils.helper_to_numeric_value(
                operation_type_values, operation["type"]
            )
            operation_json["type"] = str(operation_type)
            operations_json.append(operation_json)

        return operations_json

    def _get_groupid_from_name(self, hostgroup):
        groupid = self._zapi.hostgroup.get({"filter": {"name": hostgroup}})
        if not groupid or len(groupid) > 1:
            self._module.fail_json("Host group '%s' cannot be found" % hostgroup)
        return groupid[0]["groupid"]

    def _convert_conditions_to_json(self, filter_parameter):
        condition_type_values = [
            "old_event_tag",
            "new_event_tag",
            "new_event_host_group",
            "event_tag_pair",
            "old_event_tag_value",
            "new_event_tag_value"
        ]

        operator_values = [
            "equal",
            "not_equal",
            "like",
            "not_like"
        ]

        conditions_json = []
        for condition in filter_parameter["conditions"]:
            condition_json = {}

            condition_type = zabbix_utils.helper_to_numeric_value(
                condition_type_values, condition["type"]
            )
            condition_json["type"] = str(condition_type)

            if condition["tag"] is not None:
                condition_json["tag"] = condition["tag"]

            if condition["hostgroup"] is not None:
                condition_json["groupid"] = self._get_groupid_from_name(condition["hostgroup"])

            if condition["oldtag"] is not None:
                condition_json["oldtag"] = condition["oldtag"]

            if condition["newtag"] is not None:
                condition_json["newtag"] = condition["newtag"]

            if condition["value"] is not None:
                condition_json["value"] = condition["value"]

            if filter_parameter["evaltype"] == "custom_expression":
                if condition["formulaid"] is not None:
                    if not condition["formulaid"].isupper():
                        self._module.fail_json(
                            "A value of formulaid must be uppercase."
                        )
                    condition_json["formulaid"] = condition["formulaid"]
                else:
                    self._module.fail_json(
                        "formulaid must be defined if evaltype is 'custom_expression'."
                    )
            else:
                if condition["formulaid"] is not None:
                    self._module.warn(
                        "A value of formulaid will be ignored because evaltype is not 'custom_expression'."
                    )

            if condition["operator"] is not None:
                if (condition["type"] == "new_event_host_group"
                   and (condition["operator"] == "like" or condition["operator"] == "not_like")):
                    self._module.fail_json(
                        "A value of operator must be equal or not_equal when condition's type is 'new_event_host_group'."
                    )
                operator = zabbix_utils.helper_to_numeric_value(
                    operator_values, condition["operator"]
                )
                condition_json["operator"] = str(operator)

            conditions_json.append(condition_json)
        return conditions_json

    def _convert_filter_parameter_to_json(self, filter_parameter):
        evaltype_values = [
            "and_or",
            "and",
            "or",
            "custom_expression"
        ]

        filter_parameter_json = {}

        evaltype = zabbix_utils.helper_to_numeric_value(
            evaltype_values, filter_parameter["evaltype"]
        )
        filter_parameter_json["evaltype"] = str(evaltype)

        filter_parameter_json["conditions"] = self._convert_conditions_to_json(filter_parameter)

        if filter_parameter["formula"] is not None:
            if filter_parameter["evaltype"] == "custom_expression":
                filter_parameter_json["formula"] = filter_parameter["formula"]
            else:
                self._module.warn(
                    "A value of formula will be ignored because evaltype is not 'custom_expression'."
                )

        return filter_parameter_json

    def create_correlation(self, name, description, operations, filter_parameter, status):
        status_values = ["enabled", "disabled"]
        status_json = zabbix_utils.helper_to_numeric_value(
            status_values, status
        )

        try:
            correlation_json = {}

            correlation_json["name"] = name

            if description is not None:
                correlation_json["description"] = description

            correlation_json["operations"] = self._convert_operations_to_json(operations)

            correlation_json["filter"] = self._convert_filter_parameter_to_json(filter_parameter)

            correlation_json["status"] = status_json

            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.correlation.create(correlation_json)
            self._module.exit_json(
                changed=True, msg="Successfully created correlation"
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to create correlation: %s" % e
            )

    def check_filter_properties(self, current_filter, future_filter):
        changed = False

        if (current_filter["evaltype"] != future_filter["evaltype"]):
            changed = True

        if "formula" in future_filter.keys():
            if (current_filter["eval_formula"] != future_filter["formula"]):
                changed = True

        for condition in current_filter["conditions"]:
            # 3 means custom expression.
            if current_filter["evaltype"] != "3":
                condition.pop("formulaid")
        diff_conditions = []
        zabbix_utils.helper_compare_lists(current_filter["conditions"], future_filter["conditions"], diff_conditions)
        if len(diff_conditions) != 0:
            changed = True

        return changed

    def update_correlation(self, current_correlation, description, operations, filter_parameter, status):
        status_values = ["enabled", "disabled"]
        status_json = zabbix_utils.helper_to_numeric_value(
            status_values, status
        )

        try:
            correlation_json = {}

            if description is not None and description != current_correlation["description"]:
                correlation_json["description"] = description

            if operations is not None:
                future_operations = self._convert_operations_to_json(operations)
                diff_operations = []
                zabbix_utils.helper_compare_lists(current_correlation["operations"], future_operations, diff_operations)
                if len(diff_operations) != 0:
                    correlation_json["operations"] = future_operations

            if filter_parameter is not None:
                future_filter = self._convert_filter_parameter_to_json(filter_parameter)
                if self.check_filter_properties(current_correlation["filter"], future_filter):
                    correlation_json["filter"] = future_filter

            if str(status_json) != current_correlation["status"]:
                correlation_json["status"] = str(status_json)

            if len(correlation_json.keys()) == 0:
                self._module.exit_json(changed=False)
            else:
                correlation_json["correlationid"] = current_correlation["correlationid"]
                if self._module.check_mode:
                    self._module.exit_json(changed=True)
                self._zapi.correlation.update(correlation_json)
                self._module.exit_json(
                    changed=True, msg="Successfully updated correlation"
                )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to update correlation: %s" % e
            )


def main():
    """Main ansible module function"""

    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type="str", required=True),
            description=dict(type="str"),
            period=dict(
                type="str",
                choices=[
                    "daily",
                    "weekly",
                    "monthly",
                    "quarterly",
                    "annually"
                ],
            ),
            slo=dict(type="float"),
            effective_date=dict(type="str"),
            timezone=dict(type="str"),
            schedule=dict(
                type="list",
                options=dict(
                    period_from=dict(
                        type="int",
                        required=True
                    ),
                    period_to=dict(
                        type="int",
                        required=True
                    )
                )
            ),
            service_tags=dict(
                type="list",
                options=dict(
                    tag=dict(
                        type="str",
                        required=True
                    ),
                    operator=dict(
                        type="str",
                        choices=[
                            "equals",
                            "contains"
                        ],
                    ),
                    value=dict(type="str")
                )
            ),
            excluded_downtimes=dict(
                type="list",
                options=dict(
                    name=dict(
                        type="str",
                        required=True
                    ),
                    period_from=dict(
                        type="int",
                        required=True
                    ),
                    period_to=dict(
                        type="int",
                        required=True
                    )
                )
            ),
            status=dict(
                type="str",
                required=False,
                default="enabled",
                choices=["enabled", "disabled"],
            ),
            state=dict(
                type="str",
                required=False,
                default="present",
                choices=["present", "absent"],
            )
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    name = module.params["name"]
    description = module.params["description"]
    period = module.params["period"]
    slo = module.params["slo"]
    effective_date = module.params["effective_date"]
    timezone = module.params["timezone"]
    schedule = module.params["schedule"]
    service_tags = module.params["service_tags"]
    excluded_downtimes = module.params["excluded_downtimes"]
    status = module.params["status"]
    state = module.params["state"]

    sla_class_obj = Sla(module)
    slas = sla_class_obj.get_slas(name)

    if state == "absent":
        if len(slas) == 1:
            sla_class_obj.delete_sla(slas[0])
        else:
            module.exit_json(changed=False)
    else:
        if len(correlations) == 1:
            correlation_class_obj.update_correlation(correlations[0], description, operations, filter_parameter, status)
        else:
            correlation_class_obj.create_correlation(name, description, operations, filter_parameter, status)


if __name__ == "__main__":
    main()
