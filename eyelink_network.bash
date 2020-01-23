#!/usr/bin/env bash
[ $(id -u) -ne 0 ] && echo "ERROR: rerun; sudo $0" && exit 1
ip link set enxa0cec830fcb1 down
ip addr add 100.1.1.2/16 dev enxa0cec830fcb1 
ip link set enxa0cec830fcb1 up
ping -c1 100.1.1.1
