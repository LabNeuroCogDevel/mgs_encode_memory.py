#!/usr/bin/env bash
set -euo pipefail
trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error"' EXIT
#
# test resuming 
#

./mgs_enc_mem.py startat2 2
# subj_info/startat2/01/test_mgsenc-A_20181011/startat2_20181011_test_2_view.csv
./mgs_recall.py test 2 2
# subj_info/startat2/01/test_mgsenc-A_20181011/startat2_20181011_test_1_recall-A_20181011094848.csv
