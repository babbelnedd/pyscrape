import os
import shutil
import sys
import unittest

path = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), '..'), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

from core.helpers import utils


class RegExTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RegExTests, self).__init__(*args, **kwargs)
        self.original_png = os.path.join(os.path.join(os.path.dirname(__file__), 'images'), 'original.png')
        self.original_jpg = os.path.join(os.path.join(os.path.dirname(__file__), 'images'), 'original.jpg')
        self.expected_png = os.path.join(os.path.join(os.path.dirname(__file__), 'images'), 'expected.png')
        self.expected_jpg = os.path.join(os.path.join(os.path.dirname(__file__), 'images'), 'expected.jpg')
        self.tmp_png = os.path.join(os.path.join(os.path.dirname(__file__), 'images'), 'tmp.png')
        self.tmp_jpg = os.path.join(os.path.join(os.path.dirname(__file__), 'images'), 'tmp.jpg')

        if os.path.exists(self.tmp_jpg):
            os.remove(self.tmp_jpg)
        if os.path.exists(self.tmp_png):
            os.remove(self.tmp_png)

        shutil.copy2(self.original_jpg, self.tmp_jpg)
        shutil.copy2(self.original_png, self.tmp_png)

    def test_jpg(self):
        utils.optimize_image(self.tmp_jpg)
        self.assertEqual(os.path.getsize(self.expected_jpg), os.path.getsize(self.tmp_jpg))

    def test_png(self):
        utils.optimize_image(self.tmp_png)
        self.assertEqual(os.path.getsize(self.expected_png), os.path.getsize(self.tmp_png))


if __name__ == '__main__':
    unittest.main()