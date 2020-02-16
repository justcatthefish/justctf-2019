#!/bin/bash

###################################
# ADMIN can access only localhost #
###################################

iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

iptables -P INPUT   DROP
iptables -P FORWARD DROP
iptables -P OUTPUT  DROP

iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

iptables -A INPUT  -p tcp -m multiport --dports 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -p tcp -m multiport --sports 80 -m state --state ESTABLISHED     -j ACCEPT

iptables -A INPUT  -j DROP
iptables -A OUTPUT -j DROP

exit 0