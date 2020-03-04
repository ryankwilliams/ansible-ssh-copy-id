[![Build Status](https://travis-ci.org/ryankwilliams/ansible-ssh-copy-id.svg?branch=master)](https://travis-ci.org/ryankwilliams/ansible-ssh-copy-id)

ssh-copy-id
===========

This role provides the ability to authorize remote systems for passwordless
SSH authentication.

This role is helpful when you have a remote machine you want to use by
ansible and wish to use SSH key based authentication. It will handle setting
the SSH keys on the remote machine allowing you to create an ansible inventory
file with the remote machine. Then you can easily call any ansible playbook
against the remote machine.

Role Variables
--------------

Below are the available varaibles you will need to supply to the role.

| Variable | Description |
| --- | --- |
| hostname | remote system to connect to (FQDN or IP) |
| username | username to connect to remote system |
| password | password to connect to remote system |
| ssh_public_key | public key file (absolute path) to set into remote system |
| port | SSH port to connect to |

Example Playbook
----------------

This example play below demonstrates ansible setting up passwordless SSH
authentication on a user supplied remote machine that currently does not have
SSH key based authentication configured.

```yaml
---
- name: configure passwordless ssh authentication on a remote machine
  hosts: localhost

  roles:
    - role: ryankwilliams.ssh_copy_id
      vars:
        hostname: 127.0.0.1
        username: username
        password: password
        ssh_public_key: /home/username/.ssh/id_rsa.pub
        ssh_port: 22
```

License
-------

GPLv3

Author Information
------------------

Ryan Williams
