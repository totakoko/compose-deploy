import os
import shutil
import unittest
import compose_run

class TestComposeExec(unittest.TestCase):

  def setUp(self):
    shutil.rmtree('.tmp', True)
    os.mkdir('.tmp')
    os.mkdir('.tmp/dir')

  def test_build_mounts(self):
    self.assertEqual(compose_run.build_mounts(''), [])
    self.assertEqual(compose_run.build_mounts('Dockerfile:/key'), [
      {
        'source': 'Dockerfile',
        'destination': '/key',
        'isdir': False
      }
    ])
    self.assertEqual(compose_run.build_mounts('./:/dir/mount1,Dockerfile:/key'), [
      {
        'source': './',
        'destination': '/dir/mount1',
        'isdir': True
      },
      {
        'source': 'Dockerfile',
        'destination': '/key',
        'isdir': False
      }
    ])
    self.assertEqual(compose_run.build_mounts('./:/dir/mount1,Dockerfile:/key,.tmp/dir:/import'), [
      {
        'source': './',
        'destination': '/dir/mount1',
        'isdir': True
      },
      {
        'source': 'Dockerfile',
        'destination': '/key',
        'isdir': False
      },
      {
        'source': '.tmp/dir',
        'destination': '/import',
        'isdir': True
      }
    ])

if __name__ == '__main__':
  unittest.main()
