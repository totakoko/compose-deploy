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
    os.environ['cd_stack_api.env__API_KEY'] = '123213123'
    os.environ['cd_stack_database.env__PASSWORD'] = 'secret'
    os.environ['cd_stack_database.env__USER'] = 'postgres'
    os.environ['cd_dir1_dir2_dir3_file__TEST'] = 'blabla'
    os.environ['MODULES_ROOT'] = '.tmp/modules'
    compose_deploy.ComposeDeploy().save_env_to_files()
    with open('.tmp/modules/stack/api.env') as f:
      self.assertEqual(f.read(), 'API_KEY=123213123\n')
    with open('.tmp/modules/stack/database.env') as f:
      content = f.read()
      self.assertIn('USER=postgres\n', content)
      self.assertIn('PASSWORD=secret\n', content)
    with open('.tmp/modules/dir1/dir2/dir3/file') as f:
      self.assertEqual(f.read(), 'TEST=blabla\n')

if __name__ == '__main__':
  unittest.main()
