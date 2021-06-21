#!/usr/bin/env bash
[ $(id -u) -ne 0 ] && echo "ERROR: rerun; sudo $0" && exit 1
DEV=enxa0cec830fcb1
! ip link set $DEV down && echo "ERROR: cannot find eithernet. see ip addr list; change \$DEV" && exit 1
ip addr add 100.1.1.2/16 dev $DEV
ip link set $DEV up
ping -c1 100.1.1.1
ip addr |grep $DEV
