import os
import shutil
import unittest
import compose_run

class TestComposeExec(unittest.TestCase):

  def setUp(self):
    pass
    # shutil.rmtree('.tmp', True)
    # os.mkdir('.tmp')

  def test_build_mounts(self):
    self.assertEqual(compose_run.build_mounts(''), [])
    self.assertEqual(compose_run.build_mounts('Dockerfile:/key'), [
      {
        'source': 'Dockerfile',
        'destination': '/key'
      }
    ])
    self.assertEqual(compose_run.build_mounts('./:/dir/mount1,Dockerfile:/key'), [
      {
        'source': './',
        'destination': '/dir/mount1'
      },
      {
        'source': 'Dockerfile',
        'destination': '/key'
      }
    ])
    self.assertEqual(compose_run.build_mounts('./:/dir/mount1,Dockerfile:/key,/opt/data:/import'), [
      {
        'source': './',
        'destination': '/dir/mount1'
      },
      {
        'source': 'Dockerfile',
        'destination': '/key'
      },
      {
        'source': '/opt/data',
        'destination': '/import'
      }
    ])

if __name__ == '__main__':
  unittest.main()
