import marccd
from marccd._io import mccd
import unittest
from os.path import join, abspath, dirname

class TestIOMCCD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testImage = join(abspath(dirname(__file__)),
                             "..", "data", "e074a_off1_011.mccd")
        return

    def test_getTIFFHeader(self):
        """Confirm mccd.getTIFFHeader returns correct header"""

        result = mccd._getTIFFHeader()
        with open(self.testImage, 'rb') as mccdfile:
            expected = mccdfile.read(1024)
        self.assertEqual(1024, len(result))
        self.assertEqual(expected, result)

        return

