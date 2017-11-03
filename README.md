[![Build Status](https://travis-ci.org/rywillia/ansible-ssh-copy-id.svg?branch=master)](https://travis-ci.org/rywillia/ansible-ssh-copy-id)

SSH copy id
===========

This role will allow you to inject a SSH public key into a remote system for
pass wordless authenticaton.

Requirements
------------

Please see the metadata file for the requirements to run this role.

Role Variables
--------------

```yaml
hostname:           # remote system hostname or IP address
username:           # remote system username
password:           # remote system password
ssh_public_key:     # ssh public key to inject (include absolute path)
```

Example Playbook
----------------

```yaml
- hosts: servers
  roles:
    - {
        role: rywillia.ssh-copy-id,
        hostname: server1,
        username: username,
        password: password,
        ssh_public_key: /home/user1/.ssh/id_rsa.pub
    }
```

License
-------

GPLv3

Author Information
------------------

Ryan Williams
