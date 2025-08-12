import unittest
from os.path import abspath, basename, dirname, join

import numpy as np

import marccd


class TestMarCCD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testImage = join(abspath(dirname(__file__)), "data", "e074a_off1_011.mccd")
        return

    def test_init_empty(self):
        """Unit tests for MarCCD default empty constructor"""

        # Empty image, no attributes provided
        mccd = marccd.MarCCD()
        self.assertTrue(np.array_equal(np.empty((0, 0)), mccd.image))
        self.assertIsNone(mccd.name)
        self.assertIsNone(mccd.distance)
        self.assertIsNone(mccd.center)
        self.assertIsNone(mccd.pixelsize)
        self.assertIsNone(mccd.timestamp)
        self.assertIsNone(mccd.wavelength)
        self.assertIsNone(mccd._parsedheader)
        self.assertEqual(b"\x00" * 3072, mccd._mccdheader)

        # Empty image, provide attributes
        mccd = marccd.MarCCD(
            name="name",
            distance=200.0,
            center=(1985.3, 1975.4),
            pixelsize=(88.6, 88.6),
            timestamp="2019-1110-1553-20-765444000",
            wavelength=1.0255,
        )
        self.assertTrue(np.array_equal(np.empty((0, 0)), mccd.image))
        self.assertEqual("name", mccd.name)
        self.assertEqual(200.0, mccd.distance)
        self.assertEqual((1985.3, 1975.4), mccd.center)
        self.assertEqual((88.6, 88.6), mccd.pixelsize)
        self.assertEqual("2019-1110-1553-20-765444000", mccd.timestamp)
        self.assertEqual(1.0255, mccd.wavelength)
        self.assertEqual(b"\x00" * 3072, mccd._mccdheader)

        # Invalid data argument
        with self.assertRaises(ValueError):
            marccd.MarCCD(10)
        with self.assertRaises(ValueError):
            marccd.MarCCD(data=10)

        return

    def test_init_image(self):
        """Unit tests for initializing MarCCD from image"""

        # Initialize from image, no attributes provided
        mccd = marccd.MarCCD(self.testImage)
        self.assertFalse(np.array_equal(np.empty((0, 0)), mccd.image))
        self.assertEqual(basename(self.testImage), mccd.name)
        self.assertEqual(199.995, mccd.distance)
        self.assertEqual((1989.0, 1974.0), mccd.center)
        self.assertEqual((88.6, 88.6), mccd.pixelsize)
        self.assertEqual("2019-1110-1553-20-765444000", mccd.timestamp)
        self.assertEqual(1.0264, mccd.wavelength)
        self.assertNotEqual(b"\x00" * 3072, mccd._mccdheader)

        # Initialize from image, provide attributes to ensure they are
        # prioritized over MCCD header
        mccd = marccd.MarCCD(
            self.testImage,
            name="name",
            distance=200.0,
            center=(1985.3, 1975.4),
            pixelsize=(88.0, 88.0),
            timestamp="2019-1110-1553-21-765444000",
            wavelength=1.0255,
        )
        self.assertFalse(np.array_equal(np.empty((0, 0)), mccd.image))
        self.assertEqual("name", mccd.name)
        self.assertEqual(200.0, mccd.distance)
        self.assertEqual((1985.3, 1975.4), mccd.center)
        self.assertEqual((88.0, 88.0), mccd.pixelsize)
        self.assertEqual("2019-1110-1553-21-765444000", mccd.timestamp)
        self.assertEqual(1.0255, mccd.wavelength)
        self.assertNotEqual(b"\x00" * 3072, mccd._mccdheader)

        return

    def test_init_ndarray(self):
        """Unit tests for initializing MarCCD from ndarray"""

        randimage = np.random.randint(
            low=0, high=(2**16) - 1, size=(500, 500), dtype=np.uint16
        )

        # ndarray image, no attributes provided
        mccd = marccd.MarCCD(randimage)
        self.assertEqual((500, 500), mccd.image.shape)
        self.assertIsNone(mccd.name)
        self.assertIsNone(mccd.distance)
        self.assertIsNone(mccd.center)
        self.assertIsNone(mccd.pixelsize)
        self.assertIsNone(mccd.timestamp)
        self.assertIsNone(mccd.wavelength)
        self.assertEqual(b"\x00" * 3072, mccd._mccdheader)

        # ndarray image, provide attributes
        mccd = marccd.MarCCD(
            randimage,
            name="name",
            distance=200.0,
            center=(1985.3, 1975.4),
            pixelsize=(88.6, 88.6),
            timestamp="2019-1110-1553-21-765444000",
            wavelength=1.0255,
        )
        self.assertEqual((500, 500), mccd.image.shape)
        self.assertEqual("name", mccd.name)
        self.assertEqual(200.0, mccd.distance)
        self.assertEqual((1985.3, 1975.4), mccd.center)
        self.assertEqual((88.6, 88.6), mccd.pixelsize)
        self.assertEqual("2019-1110-1553-21-765444000", mccd.timestamp)
        self.assertEqual(1.0255, mccd.wavelength)
        self.assertEqual(b"\x00" * 3072, mccd._mccdheader)

        # providing dtype other than np.uint16 should generate warning
        randimage = np.random.randint(0, 100, (500, 500), np.int16)
        with self.assertWarns(UserWarning):
            mccd = marccd.MarCCD(randimage)

        return

    def test_dimensions(self):
        """Unit tests for MarCCD dimensions attribute"""

        for dims in [(500, 500), (0, 0), (1000, 1300)]:
            mccd = marccd.MarCCD(np.zeros(dims, dtype=np.uint16))
            self.assertEqual(dims, mccd.dimensions)

        return

    def test_repr(self):
        """Unit tests for Marccd.__repr__() method"""
        mccd = marccd.MarCCD()
        dims = mccd.dimensions
        self.assertTrue(f"<marccd.MarCCD with {dims[0]}x{dims[1]} pixels" in str(mccd))

        randimage = np.random.randint(0, 100, (500, 500), np.uint16)
        mccd = marccd.MarCCD(randimage)
        dims = mccd.dimensions
        self.assertTrue(f"<marccd.MarCCD with {dims[0]}x{dims[1]} pixels" in str(mccd))

        return

    def test_readwrite(self):
        """Unit test for MarCCD reading and writing"""
        import filecmp
        import os

        # Test round trip leaves MCCD image unchanged
        mccd = marccd.MarCCD(self.testImage)
        datadir = dirname(self.testImage)
        temp = join(datadir, "temp.mccd")
        mccd.write(temp)
        self.assertTrue(filecmp.cmp(self.testImage, temp))
        os.remove(temp)

        return
