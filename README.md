Qubes-InterVMFS
==============

A filesystem for interchanging files between virtual machines under qubes.

This is a proof on concept and not considered as stable, final, mature, secure
or whatever as a tool for qubes is expected! Try it on your own risk.

Installation
------------

the following files are required in the given places:

dom0:

	etc/qubes-rpc/qubes.QubesInterVMFS

destvm:

	usr/bin/QubesInterVMFSd.py
	etc/qubes-rpc/qubes.QubesInterVMFS

	dependency: python3

srcvm:

	usr/bin/QubesInterVMFS.py

	dependency: python3, python3-llfuser

the makefile is able to create a tgz and contains a brute force method to
compile a debian package for easier installation and deinstallation.

Running
-------

Create a directory.

Run usr/bin/QubesInterVMFS.py in the srcvm with the destvm as first and that
directory name as second argument.

The home directory of the destvm should be readonly accessible in the
directory in the srcvm.

Debugging
---------

The two parts are communicating via qrexec-client-vm (see
https://www.qubes-os.org/doc/qrexec2/) but can run standalone (directly using
stdin/out) for debugging purpose. if you add a non-zero second parameter it
will switch on debugging and run locally.

Todos
-----

- configurable shared directory

- anonymise the inodes (currently the original inodes are seen in the client)

- source code review

- native server

