import os
import shutil
import sys
import unittest

path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if not path in sys.path:
    sys.path.insert(1, path)
del path

from core.media import codec


class MkvTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MkvTests, self).__init__(*args, **kwargs)
        self.orig_mkv = os.path.join(os.path.dirname(__file__), 'videos', 'original.mkv')
        self.tmp_mkv = os.path.join(os.path.dirname(__file__), 'videos', 'tmp.mkv')

    def setUp(self):
        if os.path.exists(self.tmp_mkv):
            os.remove(self.tmp_mkv)
        shutil.copy2(self.orig_mkv, self.tmp_mkv)

    def test_vinfo(self):
        info = codec.get_ainfo(self.tmp_mkv)
        self.assertEqual(len(info), 2)
        self.assertIn('channel_count', info[0])
        self.assertIn('channel_count', info[1])
        self.assertIn('language', info[0])
        self.assertIn('language', info[1])
        self.assertIn('format', info[0])
        self.assertIn('format', info[1])
        self.assertEqual(info[0].get('channel_count'), '2')  # todo: to in
        self.assertEqual(info[1].get('channel_count'), '2')  # todo: to in
        self.assertEqual(info[0].get('format'), 'mp3')
        self.assertEqual(info[1].get('format'), 'mp3')
        self.assertEqual(info[0].get('language'), 'German')
        self.assertEqual(info[1].get('language'), 'English')

    def test_ainfo(self):
        info = codec.get_vinfo(self.tmp_mkv)
        self.assertIn('scantype', info)
        self.assertIn('fps', info)
        self.assertIn('height', info)
        self.assertIn('width', info)
        self.assertIn('codec', info)
        self.assertIn('aspect', info)
        self.assertIn('bitrate', info)

        self.assertEqual(info.get('scantype'), 'Progressive')
        self.assertEqual(info.get('fps'), '30.000')
        self.assertEqual(info.get('height'), '1080')  # todo: to int
        self.assertEqual(info.get('width'), '1920')  # todo: to int
        self.assertEqual(info.get('codec'), 'h264')
        self.assertEqual(info.get('aspect'), 1.78)
        self.assertEqual(info.get('bitrate'), '669 Kbps')

    def test_delete_audio_tracks(self):
        info = codec.get_ainfo(self.tmp_mkv)
        self.assertIn({'channel_count': '2', 'language': 'German', 'format': 'mp3'}, info)
        self.assertIn({'channel_count': '2', 'language': 'English', 'format': 'mp3'}, info)

        codec.delete_audio_tracks([self.tmp_mkv])

        info = codec.get_ainfo(self.tmp_mkv)
        self.assertIn({'channel_count': '2', 'language': 'German', 'format': 'mp3'}, info)
        self.assertNotIn({'channel_count': '2', 'language': 'English', 'format': 'mp3'}, info)
        self.assertEqual(len(info), 1)

    def test_get_runtime(self):
        runtime = codec.get_runtime([self.tmp_mkv])
        self.assertEqual(str(3.633), runtime)

if __name__ == '__main__':
    unittest.main()