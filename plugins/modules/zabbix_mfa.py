#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2024, ONODERA Masaru <masaru-onodera@ieee.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: zabbix_regexp

short_description: Create/update/delete Zabbix MFA


description:
    - This module allows you to create, update and delete Zabbix MFA.

author:
    - ONODERA Masaru(@masa-orca)

requirements:
    - "python >= 3.11"

version_added: 3.0.5

options:
    name:
        description:
            - Name of this regular expression
        type: str
        required: true
    mfa_type:
        description:
            - A test string for this regular expression
        type: str
        choices:
            - "totp"
            - "duo_universal_prompt"
    hash_function:
        description:
            - List of expressions.
        type: str
        choices:
            - "sha-1"
            - "sha-256"
            - "sha-512"
    code_length:
        description:
            - List of expressions.
        type: int
        choices:
            - 6
            - 8
    api_hostname:
        description:
            - 	API hostname provided by the Duo authentication service.
        type: str
    clientid:
        description:
            - 	API hostname provided by the Duo authentication service.
        type: str
    client_secret:
        description:
            - 	API hostname provided by the Duo authentication service.
        type: str
    state:
        description:
            - State of this MFA.
        type: str
        choices: ['present', 'absent']
        default: 'present'


notes:
    - Only Zabbix >= 7.0 is supported.
    - This module returns changed=true when I(mfa_type) is C(duo_universal_prompt) as Zabbix API
      will not return any sensitive information back for module to compare.

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

- name: Update regexp of 'File systems for discovery'
  # set task level variables as we change ansible_connection plugin here
  vars:
    ansible_network_os: community.zabbix.zabbix
    ansible_connection: httpapi
    ansible_httpapi_port: 443
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_zabbix_url_path: 'zabbixeu'  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
    ansible_host: zabbix-example-fqdn.org
  community.zabbix.zabbix_regexp:
    name: File systems for discovery
    test_string: ext2
    expressions:
      - expression: "^(btrfs|ext2|ext3|ext4|reiser|xfs|ffs|ufs|jfs|jfs2|vxfs|hfs|apfs|refs|ntfs|fat32|zfs)$"
        expression_type: result_is_true
"""

RETURN = """
msg:
    description: The result of the operation
    returned: success
    type: str
    sample: 'Successfully updated regular expression setting'
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
from ansible.module_utils.compat.version import LooseVersion

import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils


class MFA(ZabbixBase):
    def __init__(self, module, zbx=None, zapi_wrapper=None):
        super(MFA, self).__init__(module, zbx, zapi_wrapper)
        if LooseVersion(self._zbx_api_version) < LooseVersion("7.0"):
            module.fail_json(
                msg="This module doesn't support Zabbix versions lower than 7.0"
            )

    def get_mfa(self, mfa_name):
        try:
            mfas = self._zapi.mfa.get(
                {
                    "output": "extend",
                    "search": {"name": mfa_name},
                }
            )
            mfa = None
            for _mfa in mfas:
                if (_mfa["name"] == mfa_name):
                    mfa = _mfa
            return mfa
        except Exception as e:
            self._module.fail_json(
                msg="Failed to get MFA setting: %s" % e
            )

    def delete_mfa(self, mfa):
        try:
            parameter = [mfa["mfaid"]]
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.mfa.delete(parameter)
            self._module.exit_json(
                changed=True, msg="Successfully deleted MFA setting."
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to delete MFA setting: %s" % e
            )

    def _convert_to_parameter(self, name, mfa_type, hash_function, code_length, api_hostname, clientid, client_secret):
        parameter = {}
        parameter['name'] = module.params["name"]
        parameter['type'] = str(zabbix_utils.helper_to_numeric_value(
                [
                    None,
                    "totp",
                    "duo_universal_prompt"
                ],
                mfa_type
            ))
        if (mfa_type == 'totp'):
            parameter['hash_function'] = str(zabbix_utils.helper_to_numeric_value(
                [
                    None,
                    "sha-1",
                    "sha-256",
                    "sha-512"
                ],
                hash_function
            ))
            parameter['code_length'] = str(module.params["code_length"])
        else:
            parameter['api_hostname'] = str(module.params["api_hostname"])
            parameter['clientid'] = str(module.params["clientid"])
            parameter['client_secret'] = str(module.params["client_secret"])
        return parameter

    def create_mfa(self, name, mfa_type, hash_function, code_length, api_hostname, clientid, client_secret):
        parameter = _convert_to_parameter(name, mfa_type, hash_function, code_length, api_hostname, clientid, client_secret)
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.mfa.create(parameter
            )
            self._module.exit_json(
                changed=True, msg="Successfully created MFA setting."
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to create MFA setting: %s" % e
            )

    def update_mfa(self, current_mfa, name, mfa_type, hash_function, code_length, api_hostname, clientid, client_secret)
        try:
            parameter = _convert_to_parameter(name, mfa_type, hash_function, code_length, api_hostname, clientid, client_secret)
            parameter.update('mfaid', current_mfa['mfaid'])
            if (mfa_type == 'totp'
               and parameter['hash_function'] == current_mfa['hash_function']
               and parameter['code_length'] == current_mfa['code_length']):
                module.exit_json(changed=False)

            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.mfa.update(parameter)
            self._module.exit_json(
                changed=True, msg="Successfully updated MFA setting."
                )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to update MFA setting: %s" % e
            )


def main():
    """Main ansible module function"""

    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(
        dict(
            name=dict(type="str", required=True),
            mfa_type=dict(
                type="str",
                choices=[
                    "totp",
                    "duo_universal_prompt"
                ],
            ),
            hash_function=dict(
                type="str",
                choices=[
                    "sha-1",
                    "sha-256",
                    "sha-512"
                ],
            ),
            code_length=dict(
                type="int",
                choices=[6, 8],
            ),
            api_hostname=dict(type="str"),
            clientid=dict(type="str"),
            client_secret=dict(type="str"),
            state=dict(
                type="str",
                default="present",
                choices=["present", "absent"]
            )
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            [
                "mfa_type",
                "totp",
                [
                    "hash_function",
                    "code_length"
                ]
            ],
            [
                "mfa_type",
                "duo_universal_prompt",
                [
                    "api_hostname",
                    "clientid",
                    "client_secret"
                ]
            ]
        ],
        mutually_exclusive=[
            ('hash_function', 'api_hostname')
        ],
        supports_check_mode=True,
    )

    name = module.params["name"]
    mfa_type = module.params["mfa_type"]
    hash_function = module.params["hash_function"]
    code_length = module.params["code_length"]
    api_hostname = module.params["api_hostname"]
    clientid = module.params["clientid"]
    client_secret = module.params["client_secret"]
    state = module.params["state"]

    mfa_class_obj = MFA(module)
    mfa = mfa_class_obj.get_mfa(name)

    if state == "absent":
        if mfa:
            mfa_class_obj.delete_mfa(mfa)
        else:
            module.exit_json(changed=False)
    else:
        if mfa:
            mfa_class_obj.update_mfa(mfa, name, mfa_type, hash_function, code_length, api_hostname, clientid, client_secret)
        else:
            mfa_class_obj.create_mfa(name, mfa_type, hash_function, code_length, api_hostname, clientid, client_secret)


if __name__ == "__main__":
    main()
