#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import os
import re
from ansible.module_utils.basic import AnsibleModule
from ansible.errors import AnsibleError

class ComposeDeploy(object):

  def __init__(self):
    self.env_regex = re.compile('(cd_([^_]+)_([^_]+)_(.+))', re.IGNORECASE)
    self.modules_root = os.getenv('MODULES_ROOT')
    if self.modules_root is None:
      raise AnsibleError('Missing environment variable MODULES_ROOT.')
    if not os.path.isdir(self.modules_root):
      raise AnsibleError('Could not find modules root. Please ensure that `{}` is the correct path.'.format(self.modules_root))

  def run(self):
    self.save_env_to_files()
    return self.load_modules()

  def load_modules(self):
    '''
    Scan the modules root, load the metadata of each module and return everything as a fact for ansible
    '''
    modules = [dict(name=d) for d in os.listdir(self.modules_root) if os.path.isdir(os.path.join(self.modules_root, d)) and d[0] != '.']
    if not modules:
      raise AnsibleError('Could not find any module. Please ensure that `{}` is the correct path.'.format(self.modules_root))

    for module in modules:
      def isfile(filename):
        return os.path.isfile(os.path.join(self.modules_root, module['name'], filename))

      module['compose'] = isfile('docker-compose.yml')
      module['prehook'] = isfile('pre.yml')

    return modules

  def save_env_to_files(self):
    '''
    Map environment variables that begin with a prefix to the filesystem.
    '''
    env_variables_matches = [self.env_regex.search(env) for env in os.environ]
    matching_env_variables = [match.groups() for match in env_variables_matches if match]
    for (env_variable, module_name, container_name, var_name) in matching_env_variables:
      module_path = os.path.join(self.modules_root, module_name)
      if not os.path.isdir(module_path):
        raise AnsibleError('Module `{}` not found. Make sure that the directory `{}` exists.'.format(module_name, module_path))

      file_path = os.path.join(module_path, container_name + '.env')
      with open(file_path, 'a') as f:
        # print('Found env variable `{}`: updating `{}` with `{}={}`'.format(env_variable, file_path, var_name, os.environ[env_variable]))
        f.write('{}={}\n'.format(var_name, os.environ[env_variable]))

def mkdirs_p(path):
  try:
    os.makedirs(path)
  except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise


def main():
  module = AnsibleModule({})
  try:
    modules = ComposeDeploy().run()
    module.warn('{}'.format(modules))
    module.exit_json(changed=False, ansible_facts=dict(modules=modules))
  except Exception as e:
    module.fail_json(msg='{}'.format(e))

if __name__ == '__main__':
  main()
