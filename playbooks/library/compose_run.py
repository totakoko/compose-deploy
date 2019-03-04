#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import os
import re
from ansible.module_utils.basic import AnsibleModule

def build_mounts(rawmounts):
  """
  Converts a string $PWD/:/dir/mount1,Dockerfile:/key"
  """
  if not rawmounts:
    return []
  return [dict(source=mount[0], destination=mount[1], isdir=os.path.isdir(mount[0])) for mount in [rawmount.split(':') for rawmount in rawmounts.split(',')]]

def main():
  try:
    module = AnsibleModule(
      argument_spec = dict(
        rawmounts = dict(required=True)
      )
    )

    mounts = build_mounts(module.params['rawmounts'])
    module.warn('{}'.format(mounts))
    module.exit_json(changed=False, ansible_facts=dict(
      mounts=mounts
    ))
  except Exception as e:
    module.fail_json(msg=e.message)

if __name__ == '__main__':
  main()
