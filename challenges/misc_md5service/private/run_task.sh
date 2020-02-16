#!/bin/bash

# NOTE: This has to be in sync with the cgrp mount path in nsjail.cfg
CGRP="/jailed_cgroups"

# We can't remount cgroups as RW,
# so instead we mount them into a different mount point as RW...
mkdir -p $CGRP/{cpu,memory,pids}

F="rw,nosuid,nodev,noexec,relatime"

# Some systems mount cpu and cpuacct controllers in one cgroup
# so we have to handle that "gracefully"
if mount | grep 'cpu on' 2>&1 > /dev/null ; then
    mount -t cgroup -o cpu,$F cgroup $CGRP/cpu
else
    mount -t cgroup -o cpu,cpuacct,$F cgroup $CGRP/cpu
fi
mount -t cgroup -o memory,$F cgroup $CGRP/memory
mount -t cgroup -o pids,$F cgroup $CGRP/pids

# Some systems have r-x permissions on cgroup controllers directories
# even though you mount them with 'rw' option, so we fix it here
chmod 755 $CGRP/{pids,memory,cpu}

# Prepare nsjail cgroups
mkdir -p $CGRP/{cpu,memory,pids}/NSJAIL

# Allow jailed user to create child cgroups
# NOTE: it is super important NOT TO chown e.g. /cpu but /cpu/NSJAIL
chown jailed:jailed $CGRP/{cpu,memory,pids}/NSJAIL

# Create dev null
mknod -m 666 /null c 1 3

# Finally, run the jail!
su -l jailed -c 'nsjail --config /nsjail.cfg'
