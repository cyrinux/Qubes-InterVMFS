#!/usr/bin/env make -f
#
# see file:///usr/share/doc/python-llfuse-doc/html/index.html
# see https://www.qubes-os.org/doc/qrexec2/
#
.PHONY: all run dbg tgz debian

all:
	mkdir -p mnt
	python3 -u usr/bin/QubesInterVMFS.py debian-9 "`pwd`/mnt"

run:
	mkdir -p mnt
	python3 -u usr/bin/QubesInterVMFS.py targetvm "`pwd`/mnt" 1
	fusermount -u mnt

dbg:
	qvm-copy-to-vm debian-9 qubes-intervmfs_0.0_all.deb

tgz:
	tar cvzf qubes-intervmfs_0.0_all.tgz etc usr

debian:
	git checkout debian
	git rebase master
	make -f debian/Makefile
	git checkout master

