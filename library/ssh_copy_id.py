#!/usr/bin/python
import socket
from os.path import join, isfile

import paramiko
from ansible.module_utils.basic import AnsibleModule

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
    ssh_port:
        description:
            - SSH port
        required: false
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
    ssh_port: 22
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
        ssh_public_key=dict(type='str', required=True),
        ssh_port=dict(type='str', required=False)
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

    # set local variables
    hostname = module.params['hostname']
    username = module.params['username']
    password = module.params['password']
    public_key = module.params['ssh_public_key']
    port = module.params['ssh_port']

    # MODULE TASKS TO BE PERFORMED BELOW..

    # set authorized key path
    if username == 'root':
        base_dir = '/root/'
    else:
        base_dir = '/home/%s' % username
    auth_key = join(base_dir, '.ssh/authorized_keys')

    # prior to creating ssh connection via paramiko, lets verify the public
    # key supplied exists on disk
    if isfile(public_key):
        module.log('SSH public key %s exists!' % public_key)
    else:
        result['message'] = 'Unable to locate ssh public key %s' % public_key
        module.fail_json(msg=result['message'])
        module.exit_json(**result)

    # create ssh client via paramiko
    ssh_con = paramiko.SSHClient()
    ssh_con.set_missing_host_key_policy(paramiko.WarningPolicy())

    # connect to remote system
    try:
        ssh_con.connect(
            hostname=hostname,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            port=port
        )
    except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
        paramiko.SSHException, socket.error) as ex:
        result['message'] = ex
        module.fail_json(msg='Connection failed to %s' % hostname, **result)
        module.exit_json(**result)

    # create sftp client
    sftp_con = ssh_con.open_sftp()

    # read ssh public key
    with open(public_key, 'r') as fh:
        data = fh.read()

    add_key = True

    # read remote system authorized key (if applicable)
    try:
        file_reader = sftp_con.open(
            auth_key,
            mode='r'
        )
        authorized_key_data = file_reader.read()
        file_reader.close()

        # check if key already exists
        if data in authorized_key_data:
            result['message'] = 'SSH public key already injected!'
            result['changed'] = False
            module.log(result['message'])
            add_key = False
    except IOError:
        module.warn('Authorized keys file %s not found!' % auth_key)

        # make the .ssh directory
        ssh_dir = '/'.join(auth_key.split('/')[:-1])
        try:
            sftp_con.lstat(ssh_dir)
        except IOError:
            module.warn('%s user .ssh dir not found! Creating..' % username)
            sftp_con.mkdir(ssh_dir)

    # inject ssh public key into authorized keys
    if add_key:
        file_handler = sftp_con.file(
            auth_key,
            mode='a'
        )
        file_handler.write(data)
        file_handler.flush()
        file_handler.chmod(int('0600', 8))
        file_handler.close()

        result['message'] = 'SSH public key injected!'
        result['changed'] = True
        module.log(result['message'])

    # close sftp/ssh connection
    sftp_con.close()
    ssh_con.close()

    # exit with results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
