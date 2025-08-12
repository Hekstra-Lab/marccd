import marccd
from marccd._io import mccd
import unittest
import numpy as np
from os.path import join, abspath, dirname
import os

class TestIOMCCD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testImage = join(abspath(dirname(__file__)),
                             "..", "data", "e074a_off1_011.mccd")
        return

    def test_read(self):
        """Unit tests for mccd.read()"""

        # File does not exist
        with self.assertRaises(ValueError):
            mccd.read("fakefile.mccd")

        # File does exist
        image, parsed_header, metadata, mccdheader = mccd.read(self.testImage)
        self.assertIsInstance(image, np.ndarray)
        self.assertIsInstance(metadata, dict)
        self.assertIsInstance(parsed_header, dict)
        self.assertFalse("dimensions" in metadata)
        self.assertEqual(3072, len(mccdheader))

        return

    def test_write(self):
        """Unit tests for mccd.write()"""

        mccdobj = marccd.MarCCD(self.testImage)
        datadir = dirname(self.testImage)
        temp = join(datadir, "temp.mccd")
        
        # _mccdheader attribute exists
        mccd.write(mccdobj, temp)
        self.assertTrue(os.path.exists(temp))
        os.remove(temp)

        # _mccdheader attribute does not exist
        mccdobj._mccdheader = None
        with self.assertRaises(AttributeError):
            mccd.write(mccdobj, temp)
        os.remove(temp)
            
        return
    
    def test_getTIFFHeader(self):
        """Confirm mccd.getTIFFHeader returns correct header"""

        result = mccd._getTIFFHeader()
        with open(self.testImage, 'rb') as mccdfile:
            expected = mccdfile.read(1024)
        self.assertEqual(1024, len(result))
        self.assertEqual(expected, result)

        return

