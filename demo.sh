#!/bin/bash
# Fail hard and fast if any intermediate command p/usr/bin/ipeline fails
set -e
/usr/bin/ip netns add ns1
/usr/bin/ip netns add ns2
/usr/bin/ip link add h1 type veth peer name h2
/usr/bin/ip link set 'h1' netns 'ns1'
/usr/bin/ip link set 'h2' netns 'ns2'
/usr/bin/ip netns exec ns1 /usr/bin/ip addr add 10.0.0.1/24 dev h1
/usr/bin/ip netns exec ns2 /usr/bin/ip addr add 10.0.0.2/24 dev h2
/usr/bin/ip netns exec ns1 /usr/bin/ip link set dev h1 up
/usr/bin/ip netns exec ns2 /usr/bin/ip link set dev h2 up
/usr/bin/ip netns exec ns1 /usr/bin/ip link set dev lo up
/usr/bin/ip netns exec ns2 /usr/bin/ip link set dev lo up
/usr/bin/ip netns exec ns1 tc qdisc add dev h1 root netem loss 10%