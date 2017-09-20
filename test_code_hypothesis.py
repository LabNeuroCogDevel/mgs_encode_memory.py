#!/usr/bin/env python2
# run with "py.test"
from hypothesis import given
import hypothesis.strategies as st
import numpy, itertools
from mgs_task import gen_stimlist, shuf_for_ntrials

def maxrep(l):
    i=itertools.groupby(l)
    reps=[ len(list(grp)) for _,grp in i ]
    return(max(l + [0] ))

"""
generic assertion for shuf_for_ntrials, to be used with chars or nums below
"""
def shuf_for_ntrials_asserts(l):
    n=int(round(len(l)*1.5))
    s=shuf_for_ntrials(l,n)
    # its as long as it we want
    assert len(s) == n
    if(len(l)>0):
      # we dont repeat things too much
      assert maxrep(list(s)) <= maxrep(list(l))*2
      # nothing is missing
      if len(l) < n: assert set(s) == set(l) # we might be okay without this?

@given( l=st.lists( st.integers(0,1000)) )
def test_shuf_for_ntrials_nums(l):
    shuf_for_ntrials_asserts(l)

@given( l=st.lists( st.characters(min_codepoint=100,max_codepoint=1000)) )
def test_shuf_for_ntrials_chars(l):
    shuf_for_ntrials_asserts(l)
