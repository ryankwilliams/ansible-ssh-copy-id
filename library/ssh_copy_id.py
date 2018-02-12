#!/usr/bin/python
import paramiko
from ansible.module_utils.basic import AnsibleModule
from os.path import join

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['stable'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ssh_copy_id

short_description: Inject SSH public key to remote systems

version_added: "2.4"

description:
    - "Inject SSH public key for password less remote system login."

options:
    host:
        description:
            - Remote system hostname or IP address
        required: true
    username:
        description:
            - Username to login to remote system
        required: true
    password:
        description:
            - Password to login to remote system
        required: true
    ssh_public_key:
        description:
            - SSH public key (include absolute path)
        required: true

author:
    - Ryan Williams
'''

EXAMPLES = '''
# Inject SSH public key into remote system
- name: Inject SSH public key
  ssh_copy_id:
    hostname: host123
    username: username
    password: password
    ssh_public_key: /home/user/.ssh/id_rsa.pub
'''

RETURN = '''
changed:
    description: Whether the module performed an action or not
    type: bool
message:
    description: The output message that the sample module generates
    type: str
original_message:
    description: The original name param that was passed in
    type: str
'''


def run_module():
    # module arguments
    module_args = dict(
        hostname=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        ssh_public_key=dict(type='str', required=True)
    )

    # results dictionary
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # create ansible module object
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # MODULE TASKS TO BE PERFORMED BELOW..

    # set authorized key path
    if module.params['username'] == 'root':
        base_dir = '/root/'
    else:
        base_dir = '/home/%s' % module.params['username']
    auth_key = join(base_dir, '.ssh/authorized_keys')

    # create ssh client via paramiko
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    # connect to remote system
    ssh_con.connect(
        hostname=module.params['hostname'],
        username=module.params['username'],
        password=module.params['password']
    )

    # create sftp client
    sftp_con = ssh_con.open_sftp()

    # read ssh public key
    with open(module.params['ssh_public_key'], 'r') as fh:
        data = fh.read()

    # read remote system authorized key
    file_reader = sftp_con.open(
        auth_key,
        mode='r'
    )
    authorized_key_data = file_reader.read()
    file_reader.close()

    # inject ssh public key
    if data in authorized_key_data:
        result['message'] = 'SSH public key already injected!'
        result['changed'] = False
        module.log(result['message'])
    else:
        file_handler = sftp_con.file(
            auth_key,
            mode='a'
        )
        file_handler.write(data)
        file_handler.flush()
        file_handler.close()

        result['message'] = 'SSH public key injected!'
        result['changed'] = True
        module.log(result['message'])

    # close sftp connection
    sftp_con.close()

    # close ssh connection
    ssh_con.close()

    # exit with results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
