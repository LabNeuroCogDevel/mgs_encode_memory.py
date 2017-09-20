#!/usr/bin/env python2

import unittest
import numpy 
from mgs_task import shuf_for_ntrials, replace_img, gen_stimlist

class TestMGS(unittest.TestCase):
  def test_shufforntrials(self):
      l=[1,2,3,3]
      n=5
      o=shuf_for_ntrials(l,n)

      #self.assertItemsEqual(numpy.unique(l),numpy.unique(o) )
      self.assertEqual(len(o), n)

  def test_get_stimlist(self):
      img=['a','b','c','e']; pos=[0,1]; n=4
      s=gen_stimlist(img,pos,n)


      self.assertEqual(1,1)


# if we run this file, we run the tests
if __name__ == '__main__': unittest.main()
