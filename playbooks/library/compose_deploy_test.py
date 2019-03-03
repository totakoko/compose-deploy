import os
import shutil
import unittest
import compose_deploy

class TestComposeDeploy(unittest.TestCase):

  def setUp(self):
    shutil.rmtree('.tmp', True)
    os.mkdir('.tmp')

  def test_mkdirs(self):
    compose_deploy.mkdirs_p('.tmp/dir1/dir11/dir111')
    compose_deploy.mkdirs_p('.tmp/dir1/dir11/dir111')
    compose_deploy.mkdirs_p('.tmp/dir1/dir11/dir112')
    compose_deploy.mkdirs_p('.tmp/dir1/dir12/dir111')

  def test_save_env_to_files(self):
    os.environ['cd_.tmp_stack_api.env__API_KEY'] = '123213123'
    os.environ['cd_.tmp_stack_database.env__PASSWORD'] = 'secret'
    os.environ['cd_.tmp_stack_database.env__USER'] = 'postgres'
    os.environ['cd_.tmp_dir1_dir2_dir3_file__TEST'] = 'blabla'
    os.environ['MODULES_ROOT'] = '.'
    compose_deploy.ComposeDeploy().save_env_to_files()
    with open('.tmp/stack/api.env') as f:
      self.assertEqual(f.read(), 'API_KEY=123213123\n')
    with open('.tmp/stack/database.env') as f:
      content = f.read()
      self.assertIn('USER=postgres\n', content)
      self.assertIn('PASSWORD=secret\n', content)
    with open('.tmp/dir1/dir2/dir3/file') as f:
      self.assertEqual(f.read(), 'TEST=blabla\n')

if __name__ == '__main__':
  unittest.main()
