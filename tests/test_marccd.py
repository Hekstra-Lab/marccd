import marccd
import unittest
import pytest
import numpy as np
from os.path import join, abspath, dirname

class TestMarCCD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testImage = join(abspath(dirname(__file__)),
                             "data", "e074a_off1_011.mccd")
        return
    
    def test_constructor(self):
        self.assertTrue(True)
        temp = marccd.MarCCD(self.testImage)
        self.assertTrue(temp.image is not None)
        return

