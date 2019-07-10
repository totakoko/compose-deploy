import os
import shutil
import unittest
import compose_deploy

class TestComposeDeploy(unittest.TestCase):

  def setUp(self):
    shutil.rmtree('.tmp', True)
    os.mkdir('.tmp')
    os.mkdir('.tmp/modules')

  def test_mkdirs(self):
    compose_deploy.mkdirs_p('.tmp/dir1/dir11/dir111')
    compose_deploy.mkdirs_p('.tmp/dir1/dir11/dir111')
    compose_deploy.mkdirs_p('.tmp/dir1/dir11/dir112')
    compose_deploy.mkdirs_p('.tmp/dir1/dir12/dir111')

  def test_save_env_to_files(self):
    os.mkdir('.tmp/modules/api')
    os.mkdir('.tmp/modules/stack')
    os.environ['cd_stack_api_API_KEY'] = '123213123'
    os.environ['cd_stack_database_PASSWORD'] = 'secret'
    os.environ['cd_stack_database_USER'] = 'postgres'
    os.environ['cd_stack__PASSWORD'] = 'secret'
    os.environ['MODULES_ROOT'] = '.tmp/modules'
    compose_deploy.ComposeDeploy().save_env_to_files()
    with open('.tmp/modules/stack/api.env') as f:
      self.assertEqual(f.read(), 'API_KEY=123213123\n')
    with open('.tmp/modules/stack/database.env') as f:
      content = f.read()
      self.assertIn('USER=postgres\n', content)
      self.assertIn('PASSWORD=secret\n', content)
    with open('.tmp/modules/stack/.env') as f:
      self.assertEqual(f.read(), 'PASSWORD=secret\n')

if __name__ == '__main__':
  unittest.main()
