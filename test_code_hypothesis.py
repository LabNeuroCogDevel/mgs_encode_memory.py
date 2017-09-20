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

@given( l=st.lists( st.integers()) )
def test_shuf_for_ntrials(l):
    n=int(round(len(l)*1.5))
    s=shuf_for_ntrials(l,n)
    # its as long as it we want
    assert len(s) == n
    if(len(l)>0):
      # we dont repeat things too much
      assert maxrep(list(s)) <= maxrep(list(l))*2
      # nothing is missing
      # assert set(s) == set(l), we might be okay with this?
